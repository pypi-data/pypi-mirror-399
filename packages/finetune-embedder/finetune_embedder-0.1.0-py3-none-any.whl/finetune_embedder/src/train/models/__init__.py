from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, Self, cast

import torch
from torch import nn
from transformers import PreTrainedModel

from finetune_embedder.src.constants import TCModel


class Model(ABC, Generic[TCModel]):
    def __init__(self, config: TCModel):
        self.config = config

    @abstractmethod
    def to_hf_model(self) -> PreTrainedModel:  # inplace
        raise NotImplementedError()

    def save_to_hf(
        self,
        repo_dir: str,
        push: bool = False,
        **push_kwargs: Any,
    ) -> None:
        repo_dir_path = Path(repo_dir)
        self.to_hf_model().save_pretrained(repo_dir_path)
        if push:
            self.to_hf_model().push_to_hub(
                repo_dir_path.name,  # type: ignore[arg-type]
                **push_kwargs,
            )

    def to(self, device: str) -> Self:
        cast(nn.Module, self.to_hf_model()).to(device)
        return self

    @classmethod
    def from_checkpoint(
        cls,
        config: TCModel,
        checkpoint_path: str,
        device: str,
        strict: bool = True,
    ) -> "Model[TCModel]":
        model = cls(config)
        ckpt = torch.load(checkpoint_path, map_location=device)
        model.to_hf_model().load_state_dict(ckpt["model_state"], strict=strict)
        return model
