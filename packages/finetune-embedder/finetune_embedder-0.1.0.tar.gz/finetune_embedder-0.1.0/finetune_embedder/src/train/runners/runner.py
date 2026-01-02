from finetune_embedder.src.settings import (
    ConstrastiveRunnerV1Settings,
    ConstrastiveRunnerV2Settings,
)
from finetune_embedder.src.train.runners import Runner


class ConstrastiveRunnerV1(Runner[ConstrastiveRunnerV1Settings]):

    def __init__(self, settings: ConstrastiveRunnerV1Settings) -> None:
        super().__init__(settings)


class ConstrastiveRunnerV2(Runner[ConstrastiveRunnerV2Settings]):
    def __init__(self, settings: ConstrastiveRunnerV2Settings) -> None:
        super().__init__(settings)
