import logging
from datetime import datetime
from typing import Tuple, cast

import torch

from finetune_embedder.src.settings import (
    ContrastiveLossSettings,
    GraphEmbedderWrapperModelSettings,
    TrainerSettings,
)
from finetune_embedder.src.train.models.graph_embedder_hf.modeling_graph_embedder import (
    GraphEmbedderModel,
)
from finetune_embedder.src.train.trainers import Trainer

_logger = logging.getLogger(__name__)


class ProcedureContrastiveTrainer(Trainer[TrainerSettings[GraphEmbedderWrapperModelSettings, ContrastiveLossSettings]]):
    def __init__(self, config: TrainerSettings[GraphEmbedderWrapperModelSettings, ContrastiveLossSettings]):
        super().__init__(config)
        _logger.info(
            f"Initialized {self.__class__.__name__} | device={self.device} | \
            num_epochs={self.num_epochs} | save_every={self.save_every} | \
            resume_from={self.resume_from}"
        )

    def _run_name(self) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        return (
            f"{self.config.model.embedding_model.replace('/', '_')}"
            f"_bs{self.config.batch_size}"
            f"_lr{self.config.lr}"
            f"_{ts}"
        )

    def _encode(self, tokens: dict[str, torch.Tensor]) -> torch.Tensor:
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        out = self.model(**tokens)
        return cast(GraphEmbedderModel, self.model).__class__.masked_mean_pooling(
            out.last_hidden_state,
            tokens["attention_mask"],
        )

    def _step(
        self,
        batch: Tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]],
    ) -> torch.Tensor:
        q_tok, c_tok = batch

        q_emb = self._encode(q_tok)  # (B, D)
        c_emb = self._encode(c_tok)  # (B*K, D)

        B = q_emb.size(0)
        K = c_emb.size(0) // B
        D = q_emb.size(1)

        return self.loss(q_emb, c_emb.view(B, K, D))
