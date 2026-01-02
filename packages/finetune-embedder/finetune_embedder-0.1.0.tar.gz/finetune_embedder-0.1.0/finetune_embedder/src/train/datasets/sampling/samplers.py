from typing import Any, Dict, List, Optional, Tuple

from finetune_embedder.src.exceptions import MissingContextError
from finetune_embedder.src.settings import (
    NegativeSamplerSettings,
    PositiveSamplerSettings,
)
from finetune_embedder.src.train.datasets.sampling import Sampler
from finetune_embedder.src.utils import load_class


class PositiveSampler(Sampler[PositiveSamplerSettings, Dict[str, Any]]):
    def __init__(self, config: PositiveSamplerSettings, context: Optional[Dict[str, Any]]) -> None:
        super().__init__(config, context)
        self.distance = load_class(self.config.distance.module_path)(self.config.distance)

    def sample(self, item: Dict[str, Any], **kwargs: Any) -> List[str]:
        texts: List[str] = item["page_content"]
        metas: List[Dict[str, Any]] = item["metadata"]
        anchor_meta = metas[kwargs["anchor_idx"]]
        anchor_range: Tuple[int, int] = anchor_meta["step_range"]
        anchor_section = anchor_meta["section"]
        candidates = [
            i
            for i, m in enumerate(metas)
            if (
                m["section"] == anchor_section
                and self.distance(anchor_range, m["step_range"]) <= self.config.max_step_distance
            )
        ]
        candidates = list(set(candidates))
        candidates = list(dict.fromkeys(candidates))
        while len(candidates) < self.config.k:
            candidates.append(kwargs["anchor_idx"])
        positives = self.rng.sample(
            candidates,
            k=self.config.k,
        )
        assert len(positives) == self.config.k
        return [texts[i] for i in positives]


class NegativeSampler(Sampler[NegativeSamplerSettings, Dict[str, Any]]):
    def __init__(self, config: NegativeSamplerSettings, context: Optional[Dict[str, Any]]) -> None:
        super().__init__(config, context)

    def _init_components(self) -> None:
        self.by_procedure: Dict[str, List[int]] = {}
        self.by_proc_section: Dict[Tuple[str, str], List[int]] = {}
        if not self.context or "dataset" not in self.context:
            raise MissingContextError(f"{self.__class__.__name__} requires 'dataset' key in context dict. ")
        self.texts = self.context["dataset"].polars["page_content"].to_list()
        self.metas = self.context["dataset"].polars["metadata"].to_list()
        for idx, meta in enumerate(self.metas):
            proc = meta["procedure_title"]
            self.by_procedure.setdefault(proc, []).append(idx)
        self.all_indices = list(range(len(self.texts)))

    def sample(self, item: Dict[str, Any], **kwargs: Any) -> List[str]:
        metas = item["metadata"]
        anchor_meta = metas[kwargs["anchor_idx"]]
        proc = anchor_meta["procedure_title"]
        section = anchor_meta["section"]
        medium_pool = [i for i in self.by_procedure.get(proc, []) if self.metas[i]["section"] != section]
        easy_pool = [i for i in self.all_indices if self.metas[i]["procedure_title"] != proc]
        self.medium = self._sample_some(medium_pool, self.config.n_medium)
        self.easy = self._sample_some(easy_pool, self.config.n_easy)
        negatives = self.medium + self.easy
        if len(negatives) < self.config.k:
            fallback_pool = medium_pool or easy_pool
            if not fallback_pool:
                raise RuntimeError("No negatives available in dataset")
            while len(negatives) < self.config.k:
                negatives.append(self.rng.choice(fallback_pool))
        assert len(negatives) == self.config.k
        return [self.texts[i] for i in negatives]

    def _sample_some(self, pool: List[int], k: int) -> List[int]:
        if not pool:
            return []
        if len(pool) >= k:
            return self.rng.sample(pool, k)
        return pool
