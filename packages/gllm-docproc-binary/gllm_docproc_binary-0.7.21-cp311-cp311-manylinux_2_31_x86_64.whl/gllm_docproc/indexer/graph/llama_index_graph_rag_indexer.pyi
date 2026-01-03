from _typeshed import Incomplete
from gllm_datastore.graph_data_store.llama_index_graph_rag_data_store import LlamaIndexGraphRAGDataStore
from gllm_docproc.indexer.graph.graph_rag_indexer import BaseGraphRAGIndexer as BaseGraphRAGIndexer
from gllm_docproc.model.element import Element as Element
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.llms.base import BaseLLM
from llama_index.core.schema import TransformComponent as TransformComponent
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from typing import Any

logger: Incomplete

class LlamaIndexGraphRAGIndexer(BaseGraphRAGIndexer):
    """Indexer for graph RAG using LlamaIndex.

    Attributes:
        _index (PropertyGraphIndex): Property graph index.
        _graph_store (LlamaIndexGraphRAGDataStore): Storage for property graph.
    """
    def __init__(self, graph_store: LlamaIndexGraphRAGDataStore, llama_index_llm: BaseLLM | None = None, kg_extractors: list[TransformComponent] | None = None, embed_model: BaseEmbedding | None = None, vector_store: BasePydanticVectorStore | None = None, **kwargs: Any) -> None:
        """Initialize the LlamaIndexKGIndexer.

        Args:
            graph_store (LlamaIndexGraphRAGDataStore): Storage for property graph.
            llama_index_llm (BaseLLM | None, optional): Language model for LlamaIndex. Defaults to None.
            kg_extractors (list[TransformComponent] | None, optional): List of knowledge graph extractors.
                Defaults to None.
            embed_model (BaseEmbedding | None, optional): Embedding model. Defaults to None.
            vector_store (BasePydanticVectorStore | None, optional): Storage for vector data. Defaults to None.
            **kwargs (Any): Additional keyword arguments.
        """
    def index(self, elements: list[Element] | list[dict[str, Any]], **kwargs: Any) -> None:
        """Index elements into the graph.

        This method indexes elements into the graph.

        Notes:
        - Currently only Neo4jPropertyGraphStore that is supported for indexing the metadata from the TextNode.
        - The 'document_id' parameter is used to specify the document ID for the elements.
        - The 'chunk_id' parameter is used to specify the chunk ID for the elements.

        Args:
            elements (list[Element] | list[dict[str, Any]]): List of elements or list of dictionaries representing
                elements to be indexed.
            **kwargs (Any): Additional keyword arguments.
        """
    def resolve_entities(self) -> None:
        """Resolve entities in the graph.

        Currently, this method does nothing.
        """
    def delete(self, **kwargs: Any) -> None:
        """Delete elements from the knowledge graph.

        This method deletes elements from the knowledge graph based on the provided document_id.

        Args:
            **kwargs (Any): Additional keyword arguments.

        Raises:
            ValueError: If document_id is not provided.
            Exception: If an error occurs during deletion.
        """
