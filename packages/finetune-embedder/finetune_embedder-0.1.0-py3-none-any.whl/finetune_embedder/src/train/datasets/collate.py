import random
from typing import Any, Dict, List, Optional, Tuple

from finetune_embedder.src.exceptions import MissingContextError
from finetune_embedder.src.settings import (
    ContrastiveV1CollateFnSettings,
    ContrastiveV2CollateFnSettings,
)
from finetune_embedder.src.train.datasets import CollateFn
from finetune_embedder.src.utils import load_class
from transformers import AutoTokenizer, PreTrainedTokenizer


class ContrastiveV1CollateFn(CollateFn[ContrastiveV1CollateFnSettings, int]):
    def __init__(self, config: ContrastiveV1CollateFnSettings, context: Optional[Dict[str, Any]]) -> None:
        super().__init__(config, context)

    def _process_batch(self, batch: List[int]) -> Tuple[List[str], List[str]]:
        queries: List[str] = []
        chunks: List[str] = []
        for idx in batch:
            rng = random.Random(idx) if self.config.deterministic else random
            if not self.context or "dataset" not in self.context:
                raise MissingContextError(f"{self.__class__.__name__} requires 'dataset' key in context dict. ")
            group = self.context["dataset"].torch.get_group(idx)
            pages = group["page_content"]
            if len(pages) >= self.config.k and not self.config.with_replacement:
                selected = rng.sample(pages, self.config.k)
            else:
                selected = rng.choices(pages, k=self.config.k)
            chunks.extend(selected)
        return queries, chunks


class ContrastiveV2CollateFn(CollateFn[ContrastiveV2CollateFnSettings, Dict[str, Any]]):
    def __init__(self, config: ContrastiveV2CollateFnSettings, context: Optional[Dict[str, Any]]) -> None:
        super().__init__(config, context)
        self.tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer.name)
        self.positive_sampler = load_class(self.config.positive_sampler.module_path)(
            self.config.positive_sampler, self.context
        )
        self.negative_sampler = load_class(self.config.negative_sampler.module_path)(
            self.config.negative_sampler, self.context
        )
        self.positive_sampler._init_components()
        self.negative_sampler._init_components()
        self.K_pos = self.config.positive_sampler.k
        self.K_neg = self.config.negative_sampler.k
        self.K = self.K_pos + self.K_neg

    def _process_batch(self, batch: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        queries: List[str] = []
        candidates: List[str] = []
        for group in batch:
            anchor_idx = self.positive_sampler.rng.choice(range(len(group["page_content"])))
            anchor_meta = group["metadata"][anchor_idx]
            procedure_title = group["procedure_title"]
            section = anchor_meta["section"]
            query = f"Procedure: {procedure_title}\n" f"Section: {section}"
            queries.append(query)
            pos_texts = self.positive_sampler.sample(
                item=group,
                anchor_idx=anchor_idx,
            )
            assert len(pos_texts) == self.K_pos
            neg_texts = self.negative_sampler.sample(
                item=group,
                anchor_idx=anchor_idx,
            )
            assert len(neg_texts) == self.K_neg
            candidates.extend(pos_texts + neg_texts)
        return queries, candidates
