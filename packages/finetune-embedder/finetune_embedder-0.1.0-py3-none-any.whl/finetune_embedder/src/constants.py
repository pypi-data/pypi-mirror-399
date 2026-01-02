import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Tuple, TypeAlias, TypeVar

import polars as pl

if TYPE_CHECKING:
    from pydantic import BaseModel

    from finetune_embedder.src.settings import (
        CollateFnSettings,
        DatasetSettings,
        DistanceSettings,
        LossSettings,
        ModelSettings,
        RunnerSettings,
        SamplerSettings,
        TrainerSettings,
    )


def tmp() -> Tuple[str, Path]:
    CONFIG_PATH = "/home/jalal/projects/tesla-mech-agent/configs/config_finetune_embedder_train.yaml"
    DATA_DIR = Path("/home/jalal/data/tesla/ModelS")
    return CONFIG_PATH, DATA_DIR


METADATA_FIELDS = {
    "procedure_title": pl.Utf8,
    "parent_topic": pl.Utf8,
}
DATA_DIR: Path = Path("/data")

CONFIG_PATH = "/config/config.yaml"
# CONFIG_PATH, DATA_DIR = tmp()
_T = TypeVar("_T")
TDataset = TypeVar("TDataset")
TModel = TypeVar("TModel")
TCDataset = TypeVar("TCDataset", bound="DatasetSettings")
TCCollateFn = TypeVar("TCCollateFn", bound="CollateFnSettings")
TCModel = TypeVar("TCModel", bound="ModelSettings")
TCTrainer = TypeVar("TCTrainer", bound="TrainerSettings")
TCLoss = TypeVar("TCLoss", bound="LossSettings")
TCRunner = TypeVar("TCRunner", bound="RunnerSettings")
TCFromConfigMixin = TypeVar("TCFromConfigMixin", bound="BaseModel")
TCSampler = TypeVar("TCSampler", bound="SamplerSettings")
TCDistance = TypeVar("TCDistance", bound="DistanceSettings")

ParquetCompression: TypeAlias = Literal["lz4", "uncompressed", "snappy", "gzip", "brotli", "zstd"]
