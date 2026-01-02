# datasets.py
from typing import Any, Dict, List, Union, cast

import polars as pl
from torch.utils.data import Dataset as TorchDataset

from finetune_embedder.src.constants import TDataset
from finetune_embedder.src.train.datasets import TextDataset


class PolarsTextDataset(TextDataset[Union[pl.DataFrame, pl.LazyFrame]]):
    class TorchPolarsTextDataset(TorchDataset[Dict[str, Any]]):
        def __init__(self, df: pl.DataFrame):
            grouped = df.group_by(pl.col("metadata").struct.field("procedure_title")).agg(pl.all())
            self.groups: List[Dict[str, Any]] = [row for row in grouped.iter_rows(named=True)]

        def __len__(self) -> int:
            return len(self.groups)

        def __getitem__(self, idx: int) -> Dict[str, Any]:
            # return only the index
            return self.groups[idx]

    def __init__(self, service: Union[pl.DataFrame, pl.LazyFrame]):
        super().__init__(service)

    @classmethod
    def from_polars(cls, df: Union[pl.DataFrame, pl.LazyFrame]) -> "TextDataset[TDataset]":
        return cast("TextDataset[TDataset]", cls(df))

    def to_polars(self) -> pl.DataFrame:
        if isinstance(self.service, pl.LazyFrame):
            return self.service.collect()
        return self.service

    def to_torch(self) -> TorchPolarsTextDataset:
        return PolarsTextDataset.TorchPolarsTextDataset(self.polars)
