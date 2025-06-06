from unittest.mock import MagicMock

from dynamiq.components.retrievers.milvus import MilvusDocumentRetriever
from dynamiq.storages.vector import MilvusVectorStore
from dynamiq.types import Document


class TestMilvusDocumentRetriever:
    def test_run_method(self):
        mock_documents = [
            Document(id="1", content="Document 1", embedding=[0.1, 0.2, 0.3]),
            Document(id="2", content="Document 2", embedding=[0.4, 0.5, 0.6]),
        ]
        mock_vector_store = MagicMock(spec=MilvusVectorStore)
        mock_vector_store._embedding_retrieval.return_value = mock_documents

        retriever = MilvusDocumentRetriever(vector_store=mock_vector_store, filters={"field": "value"}, top_k=5)

        result = retriever.run(
            query_embedding=[0.1, 0.2, 0.3],
            exclude_document_embeddings=False,
            top_k=2,
            filters={"new_field": "new_value"},
        )

        mock_vector_store._embedding_retrieval.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            filters={"new_field": "new_value"},
            top_k=2,
            content_key=None,
            embedding_key=None,
            return_embeddings=True,
        )

        expected_documents = [
            Document(id="1", content="Document 1", embedding=[0.1, 0.2, 0.3]),
            Document(id="2", content="Document 2", embedding=[0.4, 0.5, 0.6]),
        ]
        assert result == {"documents": expected_documents}

    def test_run_method_with_defaults(self):
        mock_documents = [
            Document(id="1", content="Document 1", embedding=None),
            Document(id="2", content="Document 2", embedding=None),
        ]
        mock_filters = {"field": "value"}

        mock_vector_store = MagicMock(spec=MilvusVectorStore)
        mock_vector_store._embedding_retrieval.return_value = mock_documents

        retriever = MilvusDocumentRetriever(vector_store=mock_vector_store, filters=mock_filters, top_k=5)

        result = retriever.run(query_embedding=[0.1, 0.2, 0.3], exclude_document_embeddings=True)

        mock_vector_store._embedding_retrieval.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            filters=mock_filters,
            top_k=5,
            content_key=None,
            embedding_key=None,
            return_embeddings=False,
        )

        expected_documents = [
            Document(id="1", content="Document 1", embedding=None),
            Document(id="2", content="Document 2", embedding=None),
        ]
        assert result == {"documents": expected_documents}

    def test_run_hybrid_method(self):
        mock_documents = [
            Document(id="1", content="Document 1", embedding=None),
            Document(id="2", content="Document 2", embedding=None),
        ]

        mock_vector_store = MagicMock(spec=MilvusVectorStore)
        mock_vector_store._hybrid_retrieval.return_value = mock_documents

        retriever = MilvusDocumentRetriever(vector_store=mock_vector_store, top_k=5)

        result = retriever.run(query="Document", query_embedding=[0.1, 0.2, 0.3], exclude_document_embeddings=True)

        mock_vector_store._hybrid_retrieval.assert_called_once_with(
            query="Document",
            query_embeddings=[[0.1, 0.2, 0.3]],
            top_k=5,
            content_key=None,
            embedding_key=None,
            return_embeddings=False,
        )

        expected_documents = [
            Document(id="1", content="Document 1", embedding=None),
            Document(id="2", content="Document 2", embedding=None),
        ]
        assert result == {"documents": expected_documents}
