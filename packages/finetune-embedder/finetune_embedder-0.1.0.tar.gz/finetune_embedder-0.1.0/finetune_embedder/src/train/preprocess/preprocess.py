from typing import Any, Dict, List, Type, cast

import polars as pl

from finetune_embedder.src.train.datasets import TextDataset
from finetune_embedder.src.train.datasets.token_counter import TokenCounter
from finetune_embedder.src.train.preprocess import TextPreprocessor
from finetune_embedder.src.utils import clean_markdown_with_metadata


class MinTokenFilter(TextPreprocessor):
    def __init__(self, min_tokens: int, token_counter: TokenCounter):
        self.min_tokens = min_tokens
        self.token_counter = token_counter

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        return cast(
            TextDataset[Any],
            ds.__class__.from_polars(
                ds.polars.with_columns(pl.col("page_content").map_elements(self.token_counter.count).alias("n_tokens"))
                .filter(pl.col("n_tokens") >= self.min_tokens)
                .drop("n_tokens")
            ),
        )


class MaxTokenFilter(TextPreprocessor):
    def __init__(self, max_tokens: int, token_counter: TokenCounter):
        self.max_tokens = max_tokens
        self.token_counter = token_counter

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        return cast(
            TextDataset[Any],
            ds.__class__.from_polars(
                ds.polars.with_columns(pl.col("page_content").map_elements(self.token_counter.count).alias("n_tokens"))
                .filter(pl.col("n_tokens") <= self.max_tokens)
                .drop("n_tokens")
            ),
        )


class QuantileTokenFilter(TextPreprocessor):
    def __init__(self, q: float, token_counter: TokenCounter):
        self.q = q
        self.token_counter = token_counter

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        df = ds.polars.with_columns(pl.col("page_content").map_elements(self.token_counter.count).alias("n_tokens"))
        cutoff = df.select(pl.col("n_tokens").quantile(self.q)).item()
        return cast(
            TextDataset[Any], ds.__class__.from_polars(df.filter(pl.col("n_tokens") <= cutoff).drop("n_tokens"))
        )


class SigmaBandTokenFilter(TextPreprocessor):
    def __init__(self, z: float, token_counter: TokenCounter):
        self.z = z
        self.token_counter = token_counter

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        df = ds.polars.with_columns(pl.col("page_content").map_elements(self.token_counter.count).alias("n_tokens"))
        mu, sigma = df.select(
            pl.col("n_tokens").mean(),
            pl.col("n_tokens").std(),
        ).row(0)
        return cast(
            TextDataset[Any],
            ds.__class__.from_polars(
                df.filter(pl.col("n_tokens").is_between(mu - self.z * sigma, mu + self.z * sigma)).drop("n_tokens")
            ),
        )


class CleanMetadataPreprocessor:
    def __init__(self, metadata_fields: Dict[str, Type[pl.Utf8]]):
        self.metadata_fields = metadata_fields

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        df = ds.polars

        existing_keys = self._get_existing_metadata_keys(df)
        new_keys = list(self.metadata_fields.keys())

        df = self._extract_clean_content_and_metadata(df)
        df = self._merge_metadata(df, existing_keys, new_keys)
        df = self._add_doc_id(df, existing_keys + new_keys)

        return cast(TextDataset[Any], ds.__class__.from_polars(df))

    def _get_existing_metadata_keys(self, df: pl.DataFrame) -> List[str]:
        dtype = df.schema.get("metadata")
        if not isinstance(dtype, pl.Struct):
            raise TypeError("Expected 'metadata' column to be a pl.Struct")
        return [field.name for field in dtype.fields]

    def _extract_clean_content_and_metadata(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            pl.col("page_content")
            .map_elements(
                clean_markdown_with_metadata,
                return_dtype=pl.Struct(
                    {
                        "page_content": pl.Utf8,
                        **self.metadata_fields,
                    }
                ),
            )
            .alias("_clean")
        )

    def _merge_metadata(
        self,
        df: pl.DataFrame,
        existing_keys: List[str],
        new_keys: List[str],
    ) -> pl.DataFrame:
        return df.with_columns(
            pl.col("_clean").struct.field("page_content").alias("page_content"),
            pl.struct(
                [
                    *[pl.col("metadata").struct.field(k).alias(k) for k in existing_keys],
                    *[pl.col("_clean").struct.field(k).alias(k) for k in new_keys],
                ]
            ).alias("metadata"),
        ).drop("_clean")

    def _add_doc_id(
        self,
        df: pl.DataFrame,
        metadata_keys: List[str],
    ) -> pl.DataFrame:
        return (
            df.with_row_index()
            .with_columns(
                pl.struct(
                    [
                        pl.col("index").alias("doc_id"),
                        *[pl.col("metadata").struct.field(k).alias(k) for k in metadata_keys],
                    ]
                ).alias("metadata")
            )
            .drop("index")
        )


class PreprocessPipeline(TextPreprocessor):
    def __init__(self, steps: List[TextPreprocessor]):
        self.steps = steps

    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        current = ds
        for step in self.steps:
            current = step.apply(current)
        return current
