import logging
from abc import ABC, abstractmethod
from contextlib import nullcontext
from typing import Any, Generic, cast

import torch
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from finetune_embedder.src.constants import TCTrainer
from finetune_embedder.src.train.models import Model
from finetune_embedder.src.train.trainers.loss import Loss
from finetune_embedder.src.utils import load_class

_logger = logging.getLogger(__name__)


class Trainer(ABC, Generic[TCTrainer]):
    LOGS_PER_EPOCH = 51  # logs per epoch

    def __init__(self, config: TCTrainer):
        self.config = config
        self.run_name = self._run_name()
        self.device = self.config.device
        self.model = self._load_model().to_hf_model()
        self.optimizer = self._load_optimizer()
        self.writer = self._load_writer()
        self.num_epochs = self.config.num_epochs
        self.checkpoint_dir = self.config.checkpoint_dir
        self.save_every = self.config.save_every
        self.loss = self._load_loss()
        self.resume_from = self.config.resume_from

    @classmethod
    def get_nstep(cls, num_batches: int) -> int:
        return max(1, num_batches // cls.LOGS_PER_EPOCH)

    @abstractmethod
    def _run_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _step(self, batch: Any) -> torch.Tensor:
        raise NotImplementedError

    def _load_model(self) -> Model[Any]:
        return cast(Model[Any], load_class(self.config.model.module_path)(self.config.model).to(self.device))

    def _load_optimizer(self) -> Optimizer:
        return torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.lr,
        )

    def _load_loss(self) -> Loss[Any]:
        return cast(Loss[Any], load_class(self.config.loss.module_path)(self.config.loss))

    def _load_writer(self) -> SummaryWriter:
        log_dir = self.config.tensorboard_dir / f"runs/{self.run_name}"
        _logger.info(f"TensorBoard log dir | path={log_dir}")
        return SummaryWriter(log_dir=str(log_dir))

    def save_checkpoint(self, epoch: int) -> None:
        ckpt = {
            "epoch": epoch,
            "model_state": self.model.state_dict(),
            "optimizer_state": self.optimizer.state_dict(),
        }
        path = self.checkpoint_dir / f"{self.run_name}/epoch_{epoch:04d}.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(ckpt, path)

    def load_checkpoint(self) -> int:
        if self.resume_from:
            checkpoint_path = self.resume_from
            _logger.info(f"Loading checkpoint from {checkpoint_path}")
            ckpt = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(ckpt["model_state"])
            self.optimizer.load_state_dict(ckpt["optimizer_state"])
            _logger.info(f"Resuming training from epoch {ckpt["epoch"]}")
            return ckpt["epoch"]  # type:ignore[no-any-return]
        return 0

    def run_epoch(
        self,
        epoch: int,
        data_loader: DataLoader,
        training: bool,
    ) -> float:
        self.model.train() if training else self.model.eval()
        tag = "Train" if training else "Val"

        ctx = nullcontext() if training else torch.no_grad()
        loss_sum = 0.0
        num_batches = len(data_loader)

        for step, batch in enumerate(data_loader):
            with ctx:
                loss = self._step(batch)
            if training:
                self.optimizer.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

            loss_sum += loss.detach().item()

            if step % self.get_nstep(num_batches) == 0:
                _logger.info(
                    "%s epoch %d | step %d / %d",
                    tag,
                    epoch,
                    step,
                    num_batches,
                )

        return loss_sum / num_batches

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
    ) -> None:
        start_epoch = self.load_checkpoint()
        for epoch in range(start_epoch + 1, self.num_epochs + 1):
            train_loss = self.run_epoch(epoch, train_loader, training=True)
            val_loss = self.run_epoch(epoch, val_loader, training=False)
            _logger.info(f"[Epoch {epoch:02d}] train loss: {train_loss:4f} | val loss: {val_loss:4f}")
            self.writer.add_scalar("loss/train_epoch", train_loss, epoch)
            self.writer.add_scalar("loss/val_epoch", val_loss, epoch)
            if epoch % self.save_every == 0:
                self.save_checkpoint(epoch)
