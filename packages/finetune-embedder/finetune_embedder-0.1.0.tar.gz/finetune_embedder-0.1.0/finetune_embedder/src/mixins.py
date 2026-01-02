from abc import ABC
from typing import Generic, Self

from finetune_embedder.src.constants import TCFromConfigMixin


class FromConfigMixin(ABC, Generic[TCFromConfigMixin]):
    def __init__(self, config: TCFromConfigMixin) -> None:
        super().__init__()
        self.config = config

    @classmethod
    def from_config(
        cls,
        config: TCFromConfigMixin,
    ) -> Self:
        return cls(config)
