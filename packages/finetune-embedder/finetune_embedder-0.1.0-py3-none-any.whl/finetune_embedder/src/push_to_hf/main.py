import logging
from typing import cast

from finetune_embedder.src.settings import (
    GraphEmbedderWrapperModelSettings,
    PushToHFSettings,
)
from finetune_embedder.src.train.models.graph_embedder import GraphEmbedderWrapperModel
from finetune_embedder.src.utils import load_class

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def push_to_hf() -> None:
    logger.info("Loading PushToHFSettings")
    settings = PushToHFSettings[GraphEmbedderWrapperModelSettings]()
    logger.info(f"Loading model class from module_path={settings.model.module_path}")
    model = cast(GraphEmbedderWrapperModel, load_class(settings.model.module_path)).from_checkpoint(
        config=settings.model,
        checkpoint_path=settings.checkpoint_path,
        device=settings.device,
    )
    logger.info(f"Pushing model to Hugging Face | repo={settings.hf.repo} | revision={settings.hf.revision}")
    model.save_to_hf(
        repo_dir=settings.hf.repo,
        push=True,
        create_repo=False,
        revision=settings.hf.revision,
        private=settings.hf.private,
        commit_message=settings.hf.commit_message,
    )
    logger.info("Model successfully pushed to Hugging Face")


if __name__ == "__main__":
    push_to_hf()
