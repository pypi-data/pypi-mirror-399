import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Self,
    Tuple,
    Union,
    cast,
    overload,
)

import numpy as np
import polars as pl
import torch
from langchain_core.documents import Document
from minio import Minio
from polars._typing import ColumnNameOrSelector, IntoExpr, IntoExprColumn
from torch.utils.data import Dataset as TorchDataset
from transformers import AutoTokenizer, PreTrainedTokenizer

from finetune_embedder.src.constants import (
    _T,
    ParquetCompression,
    TCCollateFn,
    TDataset,
)
from finetune_embedder.src.settings import MinioDatasetSettings, ParquetDatasetSettings
from finetune_embedder.src.train.datasets.token_counter import TokenCounter


class Dataset(ABC, Generic[TDataset]):
    def __init__(self, service: TDataset):
        super().__init__()
        self.service = service
        self._polars: Optional[pl.DataFrame] = None
        self._torch: Optional[TorchDataset] = None

    @classmethod
    @abstractmethod
    def from_polars(cls, df: Union[pl.DataFrame, pl.LazyFrame]) -> "Dataset[TDataset]":
        raise NotImplementedError

    @abstractmethod
    def to_polars(self) -> pl.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def to_torch(self) -> TorchDataset:
        raise NotImplementedError

    @classmethod
    def from_parquet(
        cls,
        path: Union[str, Path],
        *,
        lazy: bool = True,
    ) -> "Dataset[TDataset]":
        df: Union[pl.DataFrame, pl.LazyFrame]
        if lazy:
            df = pl.scan_parquet(path)
        else:
            df = pl.read_parquet(path)

        return cls.from_polars(df)

    @property
    def polars(self) -> pl.DataFrame:
        if self._polars is None:
            self._polars = self.to_polars()
        return self._polars

    @property
    def torch(self) -> TorchDataset:
        if self._torch is None:
            self._torch = self.to_torch()
        return self._torch

    @property
    def polars_shape(self) -> Tuple[int, int]:
        return self.polars.shape

    @classmethod
    def from_documents(cls, docs: List[Document]) -> "TextDataset[TDataset]":
        df = pl.DataFrame(
            {
                "page_content": [d.page_content for d in docs],
                "metadata": [d.metadata or {} for d in docs],
            }
        )
        return cast(TextDataset[TDataset], cls.from_polars(df))

    def with_columns(
        self,
        *exprs: IntoExpr | Iterable[IntoExpr],
        **named_exprs: IntoExpr,
    ) -> "Dataset[TDataset]":
        df = self.polars.with_columns(*exprs, **named_exprs)
        return self.__class__.from_polars(df)

    def filter(
        self,
        *predicates: (IntoExprColumn | Iterable[IntoExprColumn] | bool | list[bool] | np.ndarray[Any, Any]),
        **constraints: Any,
    ) -> "Dataset[TDataset]":
        return self.__class__.from_polars(self.polars.filter(*predicates, **constraints))

    def drop(
        self,
        *columns: ColumnNameOrSelector | Iterable[ColumnNameOrSelector],
        strict: bool = True,
    ) -> "Dataset[TDataset]":
        return self.__class__.from_polars(self.polars.drop(*columns, strict=strict))

    def __len__(self) -> int:
        return self.polars_shape[0]


class TextDataset(Dataset[TDataset], Generic[TDataset]):
    REQUIRED_COLUMNS = {"page_content", "metadata"}

    def __init__(self, service: TDataset):
        super().__init__(service)
        self._validate_schema()

    def _validate_schema(self) -> None:
        df = self.polars
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"{self.__class__.__name__} requires columns {self.REQUIRED_COLUMNS}, " f"but missing {missing}"
            )

    def iter_documents(self) -> Iterator[Document]:
        for row in self.polars.iter_rows(named=True):
            yield Document(
                page_content=row["page_content"],
                metadata=row["metadata"],
            )

    def dump_documents(
        self,
        out_dir: str,
        prefix: str = "doc",
        ext: str = ".md",
        encoding: str = "utf-8",
    ) -> None:
        out_dir_path = Path(out_dir)
        out_dir_path.mkdir(parents=True, exist_ok=True)
        for i, row in enumerate(self.polars.iter_rows(named=True)):
            path = out_dir_path / f"{prefix}_{i:05d}{ext}"
            path.write_text(row["page_content"], encoding=encoding)

    def to_langchain_documents(
        self,
    ) -> list[Document]:
        docs: list[Document] = []
        for row in self.polars.iter_rows(named=True):
            docs.append(
                Document(
                    page_content=row["page_content"],
                    metadata=row["metadata"],
                )
            )
        return docs

    def to_minio(
        self,
        *,
        bucket: str,
        key: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        compression: ParquetCompression = "zstd",
        row_group_size: int = 100_000,
    ) -> None:
        client = Minio(
            endpoint_url.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=endpoint_url.startswith("https://"),
        )
        buffer = io.BytesIO()
        self.polars.write_parquet(
            buffer,
            compression=compression,
            row_group_size=row_group_size,
        )
        buffer.seek(0)
        client.put_object(
            bucket_name=bucket,
            object_name=key,
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type="application/octet-stream",
        )

    def kpis(self, token_counter: TokenCounter) -> Dict[str, float]:
        df = self.polars.with_columns(pl.col("page_content").map_elements(token_counter.count).alias("n_tokens"))
        return cast(
            Dict[str, float],
            df.select(
                num_docs=pl.len(),
                avg_tokens=pl.col("n_tokens").mean(),
                std_tokens=pl.col("n_tokens").std(),
                min_tokens=pl.col("n_tokens").min(),
                max_tokens=pl.col("n_tokens").max(),
                p95_tokens=pl.col("n_tokens").quantile(0.95),
                p98_tokens=pl.col("n_tokens").quantile(0.98),
            ).to_dicts()[0],
        )

    @overload
    @classmethod
    def from_config(
        cls,
        config: ParquetDatasetSettings,
    ) -> Self: ...

    @overload
    @classmethod
    def from_config(
        cls,
        config: MinioDatasetSettings,
    ) -> Self: ...

    @classmethod
    def from_config(
        cls,
        config: Union[ParquetDatasetSettings, MinioDatasetSettings],
    ) -> Self:
        if isinstance(config, ParquetDatasetSettings):
            df = pl.scan_parquet(config.path) if config.lazy else pl.read_parquet(config.path)
            return cast(Self, cls.from_polars(df))
        if isinstance(config, MinioDatasetSettings):
            return cast(
                Self,
                cls.from_minio(
                    bucket=config.bucket,
                    key=config.key,
                    endpoint_url=config.endpoint,
                    access_key=config.access_key,
                    secret_key=config.secret_key,
                ),
            )

        raise TypeError(f"Unsupported dataset config: {type(config).__name__}")

    @classmethod
    def from_minio(
        cls,
        *,
        bucket: str,
        key: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
    ) -> "TextDataset[TDataset]":
        client = Minio(
            endpoint_url.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=endpoint_url.startswith("https://"),
        )
        response = client.get_object(bucket, key)
        try:
            buffer = io.BytesIO(response.read())
        finally:
            response.close()
            response.release_conn()

        df = pl.read_parquet(buffer)
        return cast("TextDataset[TDataset]", cls.from_polars(df))

    @classmethod
    def from_records(
        cls,
        records: List[Tuple[str, Dict[str, Any]]],
    ) -> "TextDataset[TDataset]":
        if not records:
            raise ValueError("records must be non-empty")
        df = pl.DataFrame(
            {
                "page_content": [text for text, _ in records],
                "metadata": [meta for _, meta in records],
            }
        )
        return cast("TextDataset[TDataset]", cls.from_polars(df))


class CollateFn(ABC, Generic[TCCollateFn, _T]):

    def __init__(self, config: TCCollateFn, context: Optional[Dict[str, Any]]) -> None:
        self.config = config
        self.context = context
        self.tokenizer = self._load_tokenizer()

    @abstractmethod
    def _process_batch(self, batch: List[_T]) -> Tuple[List[str], List[str]]:
        raise NotImplementedError()

    def __call__(self, batch: List[_T]) -> Tuple[torch.Tensor, torch.Tensor]:
        queries, candidates = self._process_batch(batch)
        return self._post_process(queries, candidates)

    def _post_process(self, queries: List[str], candidates: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        queries = [f"search_query: {query}" for query in queries]
        candidates = [f"search_document: {p}" for p in candidates]
        return self._tokenizer_qc(queries, candidates)

    def _tokenizer_qc(self, queries: List[str], candidates: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        q_tok = self.tokenizer(
            queries,
            padding=self.config.tokenizer.padding,
            truncation=self.config.tokenizer.truncation,
            max_length=self.config.tokenizer.max_length,
            return_tensors="pt",
        )
        c_tok = self.tokenizer(
            candidates,
            padding=self.config.tokenizer.padding,
            truncation=self.config.tokenizer.truncation,
            max_length=self.config.tokenizer.max_length,
            return_tensors="pt",
        )
        return q_tok, c_tok

    def _load_tokenizer(self) -> PreTrainedTokenizer:
        tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer.name)
        return cast(PreTrainedTokenizer, tokenizer)
