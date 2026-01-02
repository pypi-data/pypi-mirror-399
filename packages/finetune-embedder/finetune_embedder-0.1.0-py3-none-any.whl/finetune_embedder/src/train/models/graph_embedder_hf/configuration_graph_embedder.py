from typing import Any

from transformers import AutoConfig, PretrainedConfig


class GraphEmbedderConfig(PretrainedConfig):
    model_type = "graph_embedder"

    def __init__(
        self,
        base_model_name: str = "nomic-ai/nomic-embed-text-v1.5",
        num_blocks: int = 2,
        dropout: float = 0.0,
        pooling: str = "cls",
        normalize: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.base_model_name = base_model_name
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.pooling = pooling
        self.normalize = normalize
        self.encoder_config = AutoConfig.from_pretrained(
            base_model_name,
            trust_remote_code=True,
        )
        self.auto_map = {
            "AutoConfig": "configuration_graph_embedder.GraphEmbedderConfig",
            "AutoModel": "modeling_graph_embedder.GraphEmbedderModel",
        }

    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes to the encoder config.
        Called only if normal attribute lookup fails.
        """
        if name != "encoder_config" and hasattr(self.encoder_config, name):
            return getattr(self.encoder_config, name)
        raise AttributeError(name)


GraphEmbedderConfig.register_for_auto_class()
