from typing import Any, Dict, Optional, cast

import torch
import torch.nn as nn
from torch import nn
from transformers import AutoModel, PreTrainedModel
from transformers.modeling_outputs import BaseModelOutput

from .configuration_graph_embedder import GraphEmbedderConfig


class EncoderBlock(nn.Module):
    def __init__(self, dim: int, hidden_dim: int, dropout: float):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.ReLU(),
        )
        self.norm = nn.LayerNorm(dim)
        self.dropout = nn.Dropout(dropout)
        self.proj = nn.Linear(hidden_dim, dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = self.net(x)
        x = self.dropout(x)
        x = self.proj(x)
        return cast(torch.Tensor, self.norm(x + residual))


class GraphHead(nn.Module):
    def __init__(self, dim: int, num_blocks: int = 1, dropout: float = 0):
        super().__init__()
        self.blocks = nn.Sequential(
            *[EncoderBlock(dim=dim, hidden_dim=dim, dropout=dropout) for _ in range(num_blocks)]
        )
        self.proj = nn.Linear(dim, dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.blocks(x)
        x = self.proj(x)
        return x


class GraphEmbedderModel(PreTrainedModel):
    config_class = GraphEmbedderConfig  # type: ignore[assignment]
    base_model_prefix = "model"
    _supports_attention_backend = True

    def __init__(self, config: GraphEmbedderConfig):
        super().__init__(config)

        base = AutoModel.from_config(
            config.encoder_config,
            trust_remote_code=True,
        )
        self.embedding_dim = base.config.hidden_size
        self.embeddings = base.embeddings
        self.encoder = base.encoder
        self.pooler = base.pooler
        self._init_requires_grad(self.embeddings)
        self._init_requires_grad(self.encoder)
        self._init_requires_grad(self.pooler)
        self.head = GraphHead(
            dim=self.embedding_dim,
            num_blocks=config.num_blocks,
            dropout=config.dropout,
        )
        self.emb_ln = nn.LayerNorm(self.embedding_dim)

    @classmethod
    def masked_mean_pooling(
        cls,
        hidden_states: torch.Tensor,  # (B, T, D)
        attention_mask: torch.Tensor,  # (B, T)
    ) -> torch.Tensor:
        mask = attention_mask.unsqueeze(-1).float()
        return (hidden_states * mask).sum(1) / mask.sum(1).clamp(min=1e-9)

    def _init_requires_grad(self, module: nn.Module) -> None:
        for p in module.parameters():
            p.requires_grad = False

    @property
    def tp_plan(self) -> Dict:
        # No tensor parallelism supported
        return {}

    @torch.no_grad()
    def get_hs_base_model(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Training / offline encoding path.
        NOT used by vLLM.

        Returns:
            Tensor of shape (B, D)
        """
        hidden_states = self.embeddings(input_ids)
        attention_mask = attention_mask.bool()  # (B, T)
        attention_mask = attention_mask[:, None, None, :]  # (B, 1, 1, T)
        hs = self.encoder(
            hidden_states,
            attention_mask=attention_mask,
        )
        return cast(torch.Tensor, hs)  # (B, T, D)

    def get_input_embeddings(self) -> nn.Module:
        # NomicBertModel does NOT implement get_input_embeddings
        return cast(nn.Module, self.embeddings.word_embeddings)

    def set_input_embeddings(self, value: nn.Module) -> None:
        self.embeddings.word_embeddings = value

    def forward_training(self, hs: torch.Tensor) -> torch.Tensor:
        hs = self.head(hs)
        hs = self.emb_ln(hs)
        pooled = hs[:, 0, :]  # CLS
        pooled = torch.nn.functional.normalize(pooled, dim=-1)
        return pooled  # B, D

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Any,
    ) -> BaseModelOutput:
        if attention_mask is None:
            attention_mask = torch.ones_like(input_ids, dtype=torch.bool)
        encoder_outputs = self.get_hs_base_model(input_ids, attention_mask)  # B, T, D
        token_embeddings = self.head(encoder_outputs)  # # B, T, D
        return BaseModelOutput(last_hidden_state=token_embeddings)  # B, T, D


GraphEmbedderModel.register_for_auto_class()
