from abc import ABC, abstractmethod
from typing import Generic

import torch
import torch.nn.functional as F

from finetune_embedder.src.constants import TCLoss
from finetune_embedder.src.settings import (
    ContrastiveLossSettings,
    MultiPositiveContrastiveLossSettings,
)


class Loss(ABC, Generic[TCLoss]):
    """
    Base interface for contrastive losses.
    """

    def __init__(self, config: TCLoss) -> None:
        self.config = config

    @abstractmethod
    def __call__(
        self,
        q_emb: torch.Tensor,
        c_emb: torch.Tensor,
    ) -> torch.Tensor:
        """
        Compute contrastive loss.
        q_emb: (B, D)
        c_emb: (B, K, D)
        """
        raise NotImplementedError


class ContrastiveLoss(Loss[ContrastiveLossSettings]):
    def __init__(self, config: ContrastiveLossSettings) -> None:
        self.config = config

    def __call__(
        self,
        q_emb: torch.Tensor,
        c_emb: torch.Tensor,  # (B, K, D)
    ) -> torch.Tensor:
        q_emb = F.normalize(q_emb, dim=-1)
        c_emb = F.normalize(c_emb, dim=-1)

        P, K, D = c_emb.shape
        c_flat = c_emb.view(P * K, D)  # (P*K, D)

        logits = (q_emb @ c_flat.T) / self.config.temperature  # (P, P*K)

        target = torch.zeros_like(logits)
        pos_idx = torch.arange(P, device=logits.device).unsqueeze(1) * K + torch.arange(
            K, device=logits.device
        ).unsqueeze(0)
        target.scatter_(1, pos_idx, 1.0 / K)

        loss = -(target * logits.log_softmax(dim=-1)).sum(dim=1).mean()
        return loss


class MultiPositiveContrastiveLoss(Loss[MultiPositiveContrastiveLossSettings]):
    def __init__(self, config: MultiPositiveContrastiveLossSettings) -> None:
        self.config = config

    def __call__(
        self,
        q_emb: torch.Tensor,  # (B, D)
        c_emb: torch.Tensor,  # (B, K, D)
    ) -> torch.Tensor:
        q_emb = F.normalize(q_emb, dim=-1)
        c_emb = F.normalize(c_emb, dim=-1)
        logits = torch.einsum("bd,bkd->bk", q_emb, c_emb)
        logits = logits / self.config.temperature
        log_probs = torch.log_softmax(logits, dim=-1)
        pos_mask = torch.zeros_like(log_probs)
        pos_mask[:, : self.config.K_pos] = 1.0
        loss = -(log_probs * pos_mask).sum(dim=1) / self.config.K_pos
        return loss.mean()
