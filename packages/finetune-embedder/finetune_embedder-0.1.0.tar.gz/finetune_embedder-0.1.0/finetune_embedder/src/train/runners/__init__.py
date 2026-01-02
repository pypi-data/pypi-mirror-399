import logging
from abc import ABC
from typing import Any, Generic, Tuple, cast

from torch.utils.data import DataLoader

from finetune_embedder.src.constants import TCRunner
from finetune_embedder.src.train.datasets import CollateFn, TextDataset
from finetune_embedder.src.train.trainers import Trainer
from finetune_embedder.src.utils import load_class

_logger = logging.getLogger(__name__)


class Runner(ABC, Generic[TCRunner]):
    def __init__(self, config: TCRunner):
        self.config = config

        _logger.info(f"Initializing Runner | class={self.__class__.__name__} | " f"config={type(config).__name__}")

        _logger.info("Loading dataset...")
        self.dataset = self._load_dataset()

        _logger.info("Building dataloaders...")
        self.train_loader, self.val_loader = self._load_dataloaders()

        _logger.info("Loading trainer...")
        self.trainer = self._load_trainer()

        _logger.info("Runner initialized successfully")

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------

    def _load_dataset(self) -> TextDataset[Any]:
        dataset_cls = load_class(self.config.dataset.module_path)

        _logger.info(
            f"Instantiating dataset | class={dataset_cls.__name__} | " f"module_path={self.config.dataset.module_path}"
        )

        dataset = cast(
            TextDataset[Any],
            dataset_cls.from_config(self.config.dataset),
        )

        _logger.info(f"Dataset loaded | type={type(dataset).__name__} | " f"size={len(dataset)}")

        return dataset

    # ------------------------------------------------------------------
    # Collate
    # ------------------------------------------------------------------

    def _build_collate_fn(self) -> CollateFn[Any, Any]:
        collate_cls = load_class(self.config.collate_fn.module_path)

        _logger.info(
            f"Building collate function | class={collate_cls.__name__} | "
            f"module_path={self.config.collate_fn.module_path}"
        )

        context = {"dataset": self.dataset}

        collate_fn = cast(
            CollateFn[Any, Any],
            collate_cls(self.config.collate_fn, context),
        )

        _logger.info("Collate function ready")

        return collate_fn

    # ------------------------------------------------------------------
    # Dataloaders
    # ------------------------------------------------------------------

    def _load_dataloaders(self) -> Tuple[DataLoader, DataLoader]:
        collate_fn = self._build_collate_fn()

        batch_size = self.config.trainer.batch_size
        shuffle = self.config.trainer.shuffle
        drop_last = self.config.trainer.drop_last

        _logger.info(f"Creating DataLoaders | batch_size={batch_size} | " f"shuffle={shuffle} | drop_last={drop_last}")

        train_loader: DataLoader = DataLoader(
            self.dataset.torch,
            batch_size=batch_size,
            shuffle=shuffle,
            collate_fn=collate_fn,
            drop_last=drop_last,
        )

        val_loader: DataLoader = DataLoader(
            self.dataset.torch,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=collate_fn,
            drop_last=drop_last,
        )

        _logger.info(
            f"Dataloaders built | samples={len(self.dataset.torch)} | "  # type: ignore[arg-type]
            f"train_batches={len(train_loader)} | "
            f"val_batches={len(val_loader)}"
        )

        return train_loader, val_loader

    # ------------------------------------------------------------------
    # Trainer
    # ------------------------------------------------------------------

    def _load_trainer(self) -> Trainer[Any]:
        trainer_cls = load_class(self.config.trainer.module_path)

        _logger.info(
            f"Instantiating trainer | class={trainer_cls.__name__} | " f"module_path={self.config.trainer.module_path}"
        )

        trainer = cast(
            Trainer[Any],
            trainer_cls(self.config.trainer),
        )

        _logger.info(
            f"Trainer ready | device={getattr(trainer, 'device', 'unknown')} | "
            f"epochs={getattr(trainer, 'num_epochs', 'unknown')}"
        )

        return trainer

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        _logger.info("Starting training run")

        self.trainer.fit(self.train_loader, self.val_loader)

        _logger.info("Closing TensorBoard writer")
        self.trainer.writer.close()

        _logger.info("Training run completed successfully")
