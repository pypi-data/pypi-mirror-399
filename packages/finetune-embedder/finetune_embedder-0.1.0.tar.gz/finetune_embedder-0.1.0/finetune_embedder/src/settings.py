# finetune_embedder/app/settings.py

from pathlib import Path
from typing import Generic, Optional, Tuple, Type, Union

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from finetune_embedder.src.constants import (
    CONFIG_PATH,
    DATA_DIR,
    TCCollateFn,
    TCDataset,
    TCDistance,
    TCLoss,
    TCModel,
)


class DatasetSettings(BaseSettings):
    module_path: str


class TokenizerSettings(BaseSettings):
    name: str
    padding: Union[str, bool]
    truncation: bool
    max_length: int


class SamplerSettings(BaseSettings):
    module_path: str
    seed: Optional[int]


class DistanceSettings(BaseSettings):
    module_path: str


class StepRangeDistanceSettings(DistanceSettings):
    pass


class PositiveSamplerSettings(SamplerSettings, Generic[TCDistance]):
    max_step_distance: int
    distance: TCDistance
    k: int


class NegativeSamplerSettings(SamplerSettings):
    n_easy: int
    n_medium: int
    k: int


class CollateFnSettings(BaseSettings):
    module_path: str
    tokenizer: TokenizerSettings


class ModelSettings(BaseSettings):
    module_path: str


class LossSettings(BaseSettings):
    module_path: str


class TrainerSettings(BaseSettings, Generic[TCModel, TCLoss]):
    module_path: str
    model: TCModel
    num_epochs: int
    batch_size: int
    shuffle: bool
    lr: float
    device: str
    save_every: int
    drop_last: bool
    loss: TCLoss
    checkpoint_dir: Path = DATA_DIR / "checkpoints"
    tensorboard_dir: Path = DATA_DIR / "tensorboard"
    resume_from: Optional[str] = None


class ParquetDatasetSettings(DatasetSettings):
    path: str
    lazy: bool


class MinioDatasetSettings(DatasetSettings):
    endpoint: str
    bucket: str
    key: str
    access_key: str
    secret_key: str


class ContrastiveV1CollateFnSettings(CollateFnSettings):
    k: int
    with_replacement: bool
    deterministic: bool


class ContrastiveV2CollateFnSettings(CollateFnSettings, Generic[TCDistance]):
    positive_sampler: PositiveSamplerSettings[TCDistance]
    negative_sampler: NegativeSamplerSettings
    k_anchors: int


class GraphEmbedderWrapperModelSettings(ModelSettings):
    embedding_model: str
    num_blocks: int
    dropout: float
    pooling: str
    normalize: bool


class ContrastiveLossSettings(LossSettings):
    temperature: float


class MultiPositiveContrastiveLossSettings(ContrastiveLossSettings):
    K_pos: int


class RunnerSettings(BaseSettings, Generic[TCDataset, TCCollateFn, TCModel, TCLoss]):
    dataset: TCDataset = Field(init=False)
    collate_fn: TCCollateFn = Field(init=False)
    trainer: TrainerSettings[TCModel, TCLoss] = Field(init=False)
    model_config = SettingsConfigDict(yaml_file=CONFIG_PATH)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class ConstrastiveRunnerV1Settings(
    RunnerSettings[
        ParquetDatasetSettings,
        ContrastiveV1CollateFnSettings,
        GraphEmbedderWrapperModelSettings,
        ContrastiveLossSettings,
    ]
):
    pass


class ConstrastiveRunnerV2Settings(
    RunnerSettings[
        MinioDatasetSettings,
        ContrastiveV2CollateFnSettings[StepRangeDistanceSettings],
        GraphEmbedderWrapperModelSettings,
        MultiPositiveContrastiveLossSettings,
    ]
):
    pass


class HFSettings(BaseSettings):
    repo: str
    revision: Optional[str]
    private: bool
    commit_message: Optional[str]


class PushToHFSettings(BaseSettings, Generic[TCModel]):
    checkpoint_path: str = Field(init=False)
    model: TCModel = Field(init=False)
    device: str = Field(init=False)
    hf: HFSettings = Field(init=False)

    model_config = SettingsConfigDict(
        yaml_file=CONFIG_PATH,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
