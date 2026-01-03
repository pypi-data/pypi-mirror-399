"""AsyncOpenSearchClient 단위 테스트"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from opensearch_client import BulkIndexError

# AsyncOpenSearchClient는 aiohttp가 설치된 경우에만 사용 가능
try:
    from opensearch_client.async_client import AsyncOpenSearchClient

    HAS_ASYNC = True
except ImportError:
    HAS_ASYNC = False
    AsyncOpenSearchClient = None  # type: ignore


pytestmark = pytest.mark.skipif(not HAS_ASYNC, reason="aiohttp not installed")


@pytest.fixture
def mock_async_opensearch():
    """Mock AsyncOpenSearch 클라이언트"""
    mock = MagicMock()
    mock.ping = AsyncMock(return_value=True)
    mock.info = AsyncMock(return_value={"version": {"number": "2.11.0"}})
    mock.close = AsyncMock()
    mock.indices.create = AsyncMock(return_value={"acknowledged": True})
    mock.indices.delete = AsyncMock(return_value={"acknowledged": True})
    mock.indices.exists = AsyncMock(return_value=True)
    mock.indices.refresh = AsyncMock(return_value={})
    mock.index = AsyncMock(return_value={"_id": "test-id"})
    mock.bulk = AsyncMock(
        return_value={
            "errors": False,
            "items": [{"index": {"_id": "test-id", "status": 201}}],
        }
    )
    mock.get = AsyncMock(return_value={"_source": {"text": "test"}})
    mock.delete = AsyncMock(return_value={"result": "deleted"})
    mock.search = AsyncMock(return_value={"hits": {"hits": [], "total": {"value": 0}}})
    mock.transport.perform_request = AsyncMock(return_value={"acknowledged": True})
    return mock


@pytest.fixture
def async_client(mock_async_opensearch):
    """AsyncOpenSearchClient with mocked AsyncOpenSearch"""
    with patch("opensearch_client.async_client.AsyncOpenSearch") as mock_class:
        mock_class.return_value = mock_async_opensearch
        client = AsyncOpenSearchClient(host="localhost", use_ssl=False)
        return client


class TestAsyncClientBasic:
    """기본 연결 테스트"""

    @pytest.mark.asyncio
    async def test_ping(self, async_client, mock_async_opensearch):
        result = await async_client.ping()
        assert result is True
        mock_async_opensearch.ping.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_info(self, async_client, mock_async_opensearch):
        result = await async_client.info()
        assert "version" in result
        mock_async_opensearch.info.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_async_opensearch):
        with patch("opensearch_client.async_client.AsyncOpenSearch") as mock_class:
            mock_class.return_value = mock_async_opensearch
            async with AsyncOpenSearchClient(host="localhost", use_ssl=False) as client:
                await client.ping()
            mock_async_opensearch.close.assert_awaited_once()


class TestAsyncClientIndex:
    """인덱스 관리 테스트"""

    @pytest.mark.asyncio
    async def test_create_index(self, async_client, mock_async_opensearch):
        result = await async_client.create_index("test-index", {"settings": {}})
        assert result["acknowledged"] is True
        mock_async_opensearch.indices.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_index(self, async_client, mock_async_opensearch):
        result = await async_client.delete_index("test-index")
        assert result["acknowledged"] is True
        mock_async_opensearch.indices.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_index_exists(self, async_client, mock_async_opensearch):
        result = await async_client.index_exists("test-index")
        assert result is True
        mock_async_opensearch.indices.exists.assert_awaited_once()


class TestAsyncClientDocument:
    """문서 관리 테스트"""

    @pytest.mark.asyncio
    async def test_index_document(self, async_client, mock_async_opensearch):
        result = await async_client.index_document(
            "test-index", {"text": "test"}, doc_id="doc-1"
        )
        assert result["_id"] == "test-id"
        mock_async_opensearch.index.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_bulk_index(self, async_client, mock_async_opensearch):
        result = await async_client.bulk_index(
            "test-index", [{"text": "doc1"}, {"text": "doc2"}]
        )
        assert result["errors"] is False
        mock_async_opensearch.bulk.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_bulk_index_raises_on_error(
        self, async_client, mock_async_opensearch
    ):
        mock_async_opensearch.bulk.return_value = {
            "errors": True,
            "items": [
                {"index": {"_id": "1", "status": 400, "error": {"type": "error"}}}
            ],
        }

        with pytest.raises(BulkIndexError) as exc_info:
            await async_client.bulk_index(
                "test-index", [{"text": "doc1"}], raise_on_error=True
            )
        assert exc_info.value.failed_count == 1

    @pytest.mark.asyncio
    async def test_get_document(self, async_client, mock_async_opensearch):
        result = await async_client.get_document("test-index", "doc-1")
        assert "_source" in result
        mock_async_opensearch.get.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_document(self, async_client, mock_async_opensearch):
        result = await async_client.delete_document("test-index", "doc-1")
        assert result["result"] == "deleted"
        mock_async_opensearch.delete.assert_awaited_once()


class TestAsyncClientSearch:
    """검색 테스트"""

    @pytest.mark.asyncio
    async def test_search(self, async_client, mock_async_opensearch):
        result = await async_client.search("test-index", {"query": {"match_all": {}}})
        assert "hits" in result
        mock_async_opensearch.search.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_hybrid_search(self, async_client, mock_async_opensearch):
        result = await async_client.hybrid_search(
            index_name="test-index",
            query="검색어",
            query_vector=[0.1] * 384,
            pipeline="test-pipeline",
        )
        assert "hits" in result
        mock_async_opensearch.search.assert_awaited_once()


class TestAsyncClientPipeline:
    """Search Pipeline 테스트"""

    @pytest.mark.asyncio
    async def test_create_search_pipeline(self, async_client, mock_async_opensearch):
        result = await async_client.create_search_pipeline(
            "test-pipeline", {"description": "test"}
        )
        assert result["acknowledged"] is True
        mock_async_opensearch.transport.perform_request.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_setup_hybrid_pipeline(self, async_client, mock_async_opensearch):
        result = await async_client.setup_hybrid_pipeline(
            pipeline_id="hybrid-pipe", text_weight=0.3, vector_weight=0.7
        )
        assert result["acknowledged"] is True
