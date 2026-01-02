import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple

from finetune_embedder.src.constants import _T, TCDistance, TCSampler
from finetune_embedder.src.settings import StepRangeDistanceSettings


class Sampler(ABC, Generic[TCSampler, _T]):
    RANDOM_SEED = 42

    def __init__(self, config: TCSampler, context: Optional[Dict[str, Any]]) -> None:
        self.config = config
        self.context = context
        self.rng = random.Random(self.config.seed)

    @abstractmethod
    def sample(self, item: _T, **kwargs: Any) -> List[str]:
        pass

    def _init_components(self) -> None:
        pass


class Distance(ABC, Generic[TCDistance]):
    def __init__(self, config: TCDistance) -> None:
        self.config = config

    @abstractmethod
    def __call__(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        raise NotImplementedError


class StepRangeDistance(Distance[StepRangeDistanceSettings]):
    def __init__(self, config: StepRangeDistanceSettings) -> None:
        super().__init__(config)

    def __call__(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        if a[1] < b[0]:
            return b[0] - a[1]
        if b[1] < a[0]:
            return a[0] - b[1]
        return 0
