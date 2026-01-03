"""VectorStore 단위 테스트"""

from unittest.mock import Mock

import pytest
from opensearchpy.exceptions import NotFoundError

from opensearch_client.vectorstore import SearchResult, VectorStore


class MockEmbedder:
    """테스트용 임베더"""

    dimension = 384

    def embed(self, text: str) -> list:
        return [0.1] * 384

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]


@pytest.fixture
def mock_client():
    """Mock OpenSearchClient"""
    client = Mock()
    client.index_exists.return_value = False
    client.create_index.return_value = {"acknowledged": True}
    client.setup_hybrid_pipeline.return_value = {"acknowledged": True}
    client.index_document.return_value = {"_id": "test-id-1"}
    client.bulk_index.return_value = {
        "errors": False,
        "items": [{"index": {"_id": "test-id-1", "status": 201}}],
    }
    client.refresh.return_value = {}
    return client


@pytest.fixture
def mock_embedder():
    return MockEmbedder()


@pytest.fixture
def vector_store(mock_client, mock_embedder):
    return VectorStore("test-index", mock_embedder, mock_client)


class TestVectorStoreInit:
    def test_creates_index_if_not_exists(self, mock_client, mock_embedder):
        mock_client.index_exists.return_value = False

        VectorStore("test-index", mock_embedder, mock_client)

        mock_client.create_index.assert_called_once()
        mock_client.setup_hybrid_pipeline.assert_called_once()

    def test_skips_index_creation_if_exists(self, mock_client, mock_embedder):
        mock_client.index_exists.return_value = True

        VectorStore("test-index", mock_embedder, mock_client)

        mock_client.create_index.assert_not_called()

    def test_auto_create_false_skips_setup(self, mock_client, mock_embedder):
        VectorStore("test-index", mock_embedder, mock_client, auto_create=False)

        mock_client.index_exists.assert_not_called()
        mock_client.create_index.assert_not_called()


class TestVectorStoreAdd:
    def test_add_single_text(self, vector_store, mock_client):
        result = vector_store.add(["테스트 문서"])

        assert result == ["test-id-1"]
        mock_client.bulk_index.assert_called_once()
        mock_client.refresh.assert_called_once()

    def test_add_empty_list(self, vector_store, mock_client):
        result = vector_store.add([])

        assert result == []
        mock_client.bulk_index.assert_not_called()

    def test_add_with_metadata(self, vector_store, mock_client):
        vector_store.add(["테스트 문서"], metadata=[{"category": "test"}])

        call_args = mock_client.bulk_index.call_args
        documents = call_args[0][1]
        assert documents[0]["category"] == "test"

    def test_add_with_ids(self, vector_store, mock_client):
        mock_client.bulk_index.return_value = {
            "errors": False,
            "items": [{"index": {"_id": "custom-id", "status": 201}}],
        }
        result = vector_store.add(["테스트 문서"], ids=["custom-id"])

        call_args = mock_client.bulk_index.call_args
        documents = call_args[0][1]
        assert documents[0]["_id"] == "custom-id"
        assert result == ["custom-id"]

    def test_add_one(self, vector_store, mock_client):
        result = vector_store.add_one("단일 문서", metadata={"key": "value"})

        assert result == "test-id-1"

    def test_add_metadata_length_mismatch_raises(self, vector_store):
        with pytest.raises(ValueError, match="texts와 metadata 길이가 다릅니다"):
            vector_store.add(["문서1", "문서2"], metadata=[{"key": "value"}])

    def test_add_ids_length_mismatch_raises(self, vector_store):
        with pytest.raises(ValueError, match="texts와 ids 길이가 다릅니다"):
            vector_store.add(["문서1", "문서2"], ids=["id-1"])


class TestVectorStoreSearch:
    def test_search_returns_results(self, vector_store, mock_client):
        mock_client.hybrid_search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "doc-1",
                        "_score": 0.95,
                        "_source": {
                            "content": "검색 결과 문서",
                            "embedding": [0.1] * 384,
                            "category": "test",
                        },
                    }
                ]
            }
        }

        results = vector_store.search("검색어", k=5)

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].text == "검색 결과 문서"
        assert results[0].score == 0.95
        assert results[0].metadata == {"category": "test"}
        assert results[0].id == "doc-1"

    def test_search_with_filter(self, vector_store, mock_client):
        mock_client.hybrid_search.return_value = {"hits": {"hits": []}}

        vector_store.search("검색어", filter={"term": {"category": "test"}})

        call_kwargs = mock_client.hybrid_search.call_args[1]
        assert call_kwargs["filter"] == {"term": {"category": "test"}}


class TestVectorStoreDelete:
    def test_delete_documents(self, vector_store, mock_client):
        vector_store.delete(["id-1", "id-2"])

        assert mock_client.delete_document.call_count == 2
        mock_client.refresh.assert_called()

    def test_delete_ignores_missing(self, vector_store, mock_client):
        mock_client.delete_document.side_effect = NotFoundError(
            404, "document_missing_exception", {"reason": "Document not found"}
        )

        # Should not raise
        vector_store.delete(["missing-id"])


class TestVectorStoreClear:
    def test_clear_recreates_index(self, vector_store, mock_client):
        mock_client.index_exists.return_value = True

        vector_store.clear()

        mock_client.delete_index.assert_called_with("test-index")


class TestVectorStoreCount:
    def test_count_returns_total(self, vector_store, mock_client):
        mock_client.search.return_value = {"hits": {"total": {"value": 42}}}

        count = vector_store.count()

        assert count == 42
