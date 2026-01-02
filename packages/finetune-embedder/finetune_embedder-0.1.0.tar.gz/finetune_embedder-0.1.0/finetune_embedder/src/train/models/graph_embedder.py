from transformers import PreTrainedModel

from finetune_embedder.src.settings import GraphEmbedderWrapperModelSettings
from finetune_embedder.src.train.models import Model
from finetune_embedder.src.train.models.graph_embedder_hf.configuration_graph_embedder import (
    GraphEmbedderConfig,
)
from finetune_embedder.src.train.models.graph_embedder_hf.modeling_graph_embedder import (
    GraphEmbedderModel,
)


class GraphEmbedderWrapperModel(Model[GraphEmbedderWrapperModelSettings]):
    def __init__(self, config: GraphEmbedderWrapperModelSettings):
        super().__init__(config)
        hf_config = GraphEmbedderConfig(
            base_model_name=config.embedding_model,
            num_blocks=config.num_blocks,
            dropout=config.dropout,
            pooling=config.pooling,
            normalize=config.normalize,
        )
        self.service = GraphEmbedderModel(hf_config)

    def to_hf_model(self) -> PreTrainedModel:
        return self.service
