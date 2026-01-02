import logging

from finetune_embedder.src.settings import ConstrastiveRunnerV2Settings
from finetune_embedder.src.train.runners.runner import ConstrastiveRunnerV2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

if __name__ == "__main__":
    ConstrastiveRunnerV2(ConstrastiveRunnerV2Settings()).run()
