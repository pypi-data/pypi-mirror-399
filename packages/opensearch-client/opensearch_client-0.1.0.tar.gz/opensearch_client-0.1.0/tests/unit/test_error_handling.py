"""에러 핸들링 단위 테스트"""

from unittest.mock import Mock

import pytest
from opensearchpy.exceptions import ConnectionError, NotFoundError, RequestError

from opensearch_client import BulkIndexError, OpenSearchClient
from opensearch_client.vectorstore import VectorStore


class MockEmbedder:
    """테스트용 임베더"""

    dimension = 384

    def embed(self, text: str) -> list:
        return [0.1] * 384

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]


class TestBulkIndexErrorHandling:
    """bulk_index 에러 처리 테스트"""

    def test_bulk_index_raises_on_partial_failure(self):
        """부분 실패 시 BulkIndexError 발생"""
        client = OpenSearchClient(host="localhost", use_ssl=False)
        mock_opensearch = Mock()
        mock_opensearch.bulk.return_value = {
            "errors": True,
            "items": [
                {"index": {"_id": "1", "status": 201}},
                {
                    "index": {
                        "_id": "2",
                        "status": 400,
                        "error": {"type": "mapper_parsing_exception"},
                    }
                },
            ],
        }
        client._client = mock_opensearch

        with pytest.raises(BulkIndexError) as exc_info:
            client.bulk_index(
                "test-index",
                [{"text": "doc1"}, {"text": "doc2"}],
                raise_on_error=True,
            )

        assert exc_info.value.failed_count == 1
        assert len(exc_info.value.failed_items) == 1
        assert "mapper_parsing_exception" in str(exc_info.value.failed_items[0])

    def test_bulk_index_no_error_when_raise_disabled(self):
        """raise_on_error=False면 예외 발생 안함"""
        client = OpenSearchClient(host="localhost", use_ssl=False)
        mock_opensearch = Mock()
        mock_opensearch.bulk.return_value = {
            "errors": True,
            "items": [
                {
                    "index": {
                        "_id": "1",
                        "status": 400,
                        "error": {"type": "some_error"},
                    }
                },
            ],
        }
        client._client = mock_opensearch

        # Should not raise
        result = client.bulk_index(
            "test-index", [{"text": "doc1"}], raise_on_error=False
        )
        assert result["errors"] is True

    def test_bulk_index_success(self):
        """성공 시 정상 반환"""
        client = OpenSearchClient(host="localhost", use_ssl=False)
        mock_opensearch = Mock()
        mock_opensearch.bulk.return_value = {
            "errors": False,
            "items": [{"index": {"_id": "1", "status": 201}}],
        }
        client._client = mock_opensearch

        result = client.bulk_index(
            "test-index", [{"text": "doc1"}], raise_on_error=True
        )
        assert result["errors"] is False


class TestVectorStoreErrorHandling:
    """VectorStore 에러 처리 테스트"""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenSearchClient"""
        client = Mock()
        client.index_exists.return_value = False
        client.create_index.return_value = {"acknowledged": True}
        client.setup_hybrid_pipeline.return_value = {"acknowledged": True}
        client.bulk_index.return_value = {
            "errors": False,
            "items": [{"index": {"_id": "test-id-1", "status": 201}}],
        }
        client.refresh.return_value = {}
        return client

    @pytest.fixture
    def mock_embedder(self):
        return MockEmbedder()

    def test_pipeline_creation_ignores_already_exists(self, mock_embedder):
        """파이프라인이 이미 존재하면 무시"""
        client = Mock()
        client.index_exists.return_value = True
        client.setup_hybrid_pipeline.side_effect = RequestError(
            400, "resource_already_exists_exception", {}
        )

        # Should not raise - resource_already_exists is ignored
        store = VectorStore("test-index", mock_embedder, client)
        assert store is not None

    def test_pipeline_creation_raises_other_request_errors(self, mock_embedder):
        """다른 RequestError는 발생"""
        client = Mock()
        client.index_exists.return_value = True
        client.setup_hybrid_pipeline.side_effect = RequestError(
            400, "invalid_pipeline", {}
        )

        with pytest.raises(RequestError):
            VectorStore("test-index", mock_embedder, client)

    def test_delete_ignores_not_found(self, mock_client, mock_embedder):
        """삭제 시 NotFoundError는 무시"""
        mock_client.delete_document.side_effect = NotFoundError(
            404, "document_missing_exception", {}
        )

        store = VectorStore("test-index", mock_embedder, mock_client)
        # Should not raise
        store.delete(["missing-id-1", "missing-id-2"])

        # delete_document은 두 번 호출됨
        assert mock_client.delete_document.call_count == 2

    def test_delete_raises_other_exceptions(self, mock_client, mock_embedder):
        """삭제 시 다른 예외는 발생"""
        mock_client.delete_document.side_effect = ConnectionError("Connection refused")

        store = VectorStore("test-index", mock_embedder, mock_client)

        with pytest.raises(ConnectionError):
            store.delete(["some-id"])


class TestExceptionAttributes:
    """예외 클래스 속성 테스트"""

    def test_bulk_index_error_str(self):
        """BulkIndexError 문자열 표현"""
        error = BulkIndexError(
            "Failed to index documents",
            [
                {"index": {"error": {"type": "error1"}}},
                {"index": {"error": {"type": "error2"}}},
            ],
        )

        assert "Failed to index documents" in str(error)
        assert "failed: 2 documents" in str(error)

    def test_bulk_index_error_attributes(self):
        """BulkIndexError 속성 접근"""
        failed_items = [{"index": {"_id": "1", "error": {"type": "error1"}}}]
        error = BulkIndexError("Test error", failed_items)

        assert error.failed_count == 1
        assert error.failed_items == failed_items
