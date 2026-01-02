from abc import ABC, abstractmethod
from typing import Any

from finetune_embedder.src.train.datasets import TextDataset


class TextPreprocessor(ABC):

    @abstractmethod
    def apply(self, ds: TextDataset[Any]) -> TextDataset[Any]:
        raise NotImplementedError
