"""OpenSearchClient 유닛 테스트"""

from unittest.mock import MagicMock, patch

import pytest

from opensearch_client.client import OpenSearchClient
from opensearch_client.exceptions import BulkIndexError


class TestOpenSearchClientInit:
    """OpenSearchClient 초기화 테스트"""

    @pytest.fixture
    def mock_opensearch(self):
        """OpenSearch 클라이언트 모킹"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            yield mock

    def test_default_initialization(self, mock_opensearch):
        """기본 초기화"""
        OpenSearchClient()
        mock_opensearch.assert_called_once()
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["hosts"] == [{"host": "localhost", "port": 9200}]
        assert call_kwargs["use_ssl"] is True
        assert call_kwargs["verify_certs"] is False

    def test_custom_host_and_port(self, mock_opensearch):
        """커스텀 호스트와 포트"""
        OpenSearchClient(host="opensearch.example.com", port=9300)
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["hosts"] == [
            {"host": "opensearch.example.com", "port": 9300}
        ]

    def test_with_authentication(self, mock_opensearch):
        """인증 정보 사용"""
        OpenSearchClient(user="admin", password="secret")
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["http_auth"] == ("admin", "secret")

    def test_without_authentication(self, mock_opensearch):
        """인증 정보 없음"""
        OpenSearchClient()
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["http_auth"] is None

    def test_partial_authentication_ignored(self, mock_opensearch):
        """부분 인증 정보는 무시"""
        OpenSearchClient(user="admin")  # password 없음
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["http_auth"] is None

    def test_ssl_configuration(self, mock_opensearch):
        """SSL 설정"""
        OpenSearchClient(use_ssl=False, verify_certs=True)
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["use_ssl"] is False
        assert call_kwargs["verify_certs"] is True

    def test_additional_kwargs_passed(self, mock_opensearch):
        """추가 kwargs 전달"""
        OpenSearchClient(timeout=30, max_retries=5)
        call_kwargs = mock_opensearch.call_args[1]
        assert call_kwargs["timeout"] == 30
        assert call_kwargs["max_retries"] == 5


class TestOpenSearchClientBasic:
    """기본 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_raw_client(self, client):
        """raw_client 속성"""
        os_client, mock_instance = client
        assert os_client.raw_client == mock_instance

    def test_ping(self, client):
        """ping 메서드"""
        os_client, mock_instance = client
        mock_instance.ping.return_value = True
        assert os_client.ping() is True
        mock_instance.ping.assert_called_once()

    def test_info(self, client):
        """info 메서드"""
        os_client, mock_instance = client
        mock_instance.info.return_value = {"cluster_name": "test"}
        result = os_client.info()
        assert result == {"cluster_name": "test"}
        mock_instance.info.assert_called_once()


class TestOpenSearchClientIndex:
    """인덱스 관련 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_create_index_without_body(self, client):
        """body 없이 인덱스 생성"""
        os_client, mock_instance = client
        mock_instance.indices.create.return_value = {"acknowledged": True}
        result = os_client.create_index("test-index")
        mock_instance.indices.create.assert_called_once_with(
            index="test-index", body={}
        )
        assert result == {"acknowledged": True}

    def test_create_index_with_body(self, client):
        """body와 함께 인덱스 생성"""
        os_client, mock_instance = client
        body = {"settings": {"index": {"knn": True}}}
        os_client.create_index("test-index", body)
        mock_instance.indices.create.assert_called_once_with(
            index="test-index", body=body
        )

    def test_delete_index(self, client):
        """인덱스 삭제"""
        os_client, mock_instance = client
        mock_instance.indices.delete.return_value = {"acknowledged": True}
        result = os_client.delete_index("test-index")
        mock_instance.indices.delete.assert_called_once_with(index="test-index")
        assert result == {"acknowledged": True}

    def test_index_exists_true(self, client):
        """인덱스 존재 확인 - 존재함"""
        os_client, mock_instance = client
        mock_instance.indices.exists.return_value = True
        assert os_client.index_exists("test-index") is True
        mock_instance.indices.exists.assert_called_once_with(index="test-index")

    def test_index_exists_false(self, client):
        """인덱스 존재 확인 - 존재하지 않음"""
        os_client, mock_instance = client
        mock_instance.indices.exists.return_value = False
        assert os_client.index_exists("test-index") is False

    def test_refresh(self, client):
        """인덱스 새로고침"""
        os_client, mock_instance = client
        mock_instance.indices.refresh.return_value = {"_shards": {"total": 1}}
        result = os_client.refresh("test-index")
        mock_instance.indices.refresh.assert_called_once_with(index="test-index")
        assert result == {"_shards": {"total": 1}}


class TestOpenSearchClientDocument:
    """문서 관련 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_index_document_without_id(self, client):
        """ID 없이 문서 인덱싱"""
        os_client, mock_instance = client
        doc = {"title": "Test"}
        mock_instance.index.return_value = {"_id": "auto-id"}
        result = os_client.index_document("test-index", doc)
        mock_instance.index.assert_called_once_with(
            index="test-index", body=doc, id=None
        )
        assert result == {"_id": "auto-id"}

    def test_index_document_with_id(self, client):
        """ID와 함께 문서 인덱싱"""
        os_client, mock_instance = client
        doc = {"title": "Test"}
        os_client.index_document("test-index", doc, doc_id="doc-1")
        mock_instance.index.assert_called_once_with(
            index="test-index", body=doc, id="doc-1"
        )

    def test_get_document(self, client):
        """문서 조회"""
        os_client, mock_instance = client
        mock_instance.get.return_value = {"_source": {"title": "Test"}}
        result = os_client.get_document("test-index", "doc-1")
        mock_instance.get.assert_called_once_with(index="test-index", id="doc-1")
        assert result == {"_source": {"title": "Test"}}

    def test_delete_document(self, client):
        """문서 삭제"""
        os_client, mock_instance = client
        mock_instance.delete.return_value = {"result": "deleted"}
        result = os_client.delete_document("test-index", "doc-1")
        mock_instance.delete.assert_called_once_with(index="test-index", id="doc-1")
        assert result == {"result": "deleted"}


class TestOpenSearchClientBulkIndex:
    """bulk_index 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_bulk_index_success(self, client):
        """벌크 인덱싱 성공"""
        os_client, mock_instance = client
        mock_instance.bulk.return_value = {"errors": False, "items": []}
        docs = [{"title": "Doc 1"}, {"title": "Doc 2"}]
        result = os_client.bulk_index("test-index", docs)
        assert result["errors"] is False
        mock_instance.bulk.assert_called_once()

    def test_bulk_index_with_id_field(self, client):
        """ID 필드를 사용한 벌크 인덱싱"""
        os_client, mock_instance = client
        mock_instance.bulk.return_value = {"errors": False, "items": []}
        docs = [{"id": "doc-1", "title": "Doc 1"}, {"id": "doc-2", "title": "Doc 2"}]
        os_client.bulk_index("test-index", docs, id_field="id")

        call_args = mock_instance.bulk.call_args[1]
        actions = call_args["body"]
        # 첫 번째 문서의 action에 _id가 있어야 함
        assert actions[0]["index"]["_id"] == "doc-1"
        assert actions[2]["index"]["_id"] == "doc-2"

    def test_bulk_index_partial_failure_no_raise(self, client):
        """부분 실패 - 예외 발생 안함"""
        os_client, mock_instance = client
        mock_instance.bulk.return_value = {
            "errors": True,
            "items": [
                {"index": {"_id": "1", "status": 201}},
                {"index": {"_id": "2", "status": 400, "error": {"reason": "failed"}}},
            ],
        }
        docs = [{"title": "Doc 1"}, {"title": "Doc 2"}]
        result = os_client.bulk_index("test-index", docs, raise_on_error=False)
        assert result["errors"] is True

    def test_bulk_index_partial_failure_raise(self, client):
        """부분 실패 - 예외 발생"""
        os_client, mock_instance = client
        mock_instance.bulk.return_value = {
            "errors": True,
            "items": [
                {"index": {"_id": "1", "status": 201}},
                {"index": {"_id": "2", "status": 400, "error": {"reason": "failed"}}},
            ],
        }
        docs = [{"title": "Doc 1"}, {"title": "Doc 2"}]
        with pytest.raises(BulkIndexError) as exc_info:
            os_client.bulk_index("test-index", docs, raise_on_error=True)
        assert exc_info.value.failed_count == 1

    def test_bulk_index_builds_correct_actions(self, client):
        """올바른 action 형식 생성"""
        os_client, mock_instance = client
        mock_instance.bulk.return_value = {"errors": False, "items": []}
        docs = [{"title": "Doc 1"}]
        os_client.bulk_index("test-index", docs)

        call_args = mock_instance.bulk.call_args[1]
        actions = call_args["body"]
        # action, document 쌍으로 구성
        assert len(actions) == 2
        assert actions[0] == {"index": {"_index": "test-index"}}
        assert actions[1] == {"title": "Doc 1"}


class TestOpenSearchClientSearch:
    """검색 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_search(self, client):
        """기본 검색"""
        os_client, mock_instance = client
        mock_instance.search.return_value = {"hits": {"hits": []}}
        body = {"query": {"match_all": {}}}
        result = os_client.search("test-index", body)
        mock_instance.search.assert_called_once_with(index="test-index", body=body)
        assert result == {"hits": {"hits": []}}

    def test_search_with_kwargs(self, client):
        """추가 옵션과 함께 검색"""
        os_client, mock_instance = client
        mock_instance.search.return_value = {"hits": {"hits": []}}
        body = {"query": {"match_all": {}}}
        os_client.search("test-index", body, size=10, from_=0)
        mock_instance.search.assert_called_once_with(
            index="test-index", body=body, size=10, from_=0
        )


class TestOpenSearchClientPipeline:
    """Search Pipeline 메서드 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_create_search_pipeline(self, client):
        """Search Pipeline 생성"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"acknowledged": True}
        body = {"phase_results_processors": []}
        result = os_client.create_search_pipeline("my-pipeline", body)
        mock_instance.transport.perform_request.assert_called_once_with(
            "PUT", "/_search/pipeline/my-pipeline", body=body
        )
        assert result == {"acknowledged": True}

    def test_delete_search_pipeline(self, client):
        """Search Pipeline 삭제"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"acknowledged": True}
        result = os_client.delete_search_pipeline("my-pipeline")
        mock_instance.transport.perform_request.assert_called_once_with(
            "DELETE", "/_search/pipeline/my-pipeline"
        )
        assert result == {"acknowledged": True}

    def test_get_search_pipeline(self, client):
        """Search Pipeline 조회"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"my-pipeline": {}}
        result = os_client.get_search_pipeline("my-pipeline")
        mock_instance.transport.perform_request.assert_called_once_with(
            "GET", "/_search/pipeline/my-pipeline"
        )
        assert result == {"my-pipeline": {}}


class TestOpenSearchClientHybridSearch:
    """하이브리드 검색 테스트"""

    @pytest.fixture
    def client(self):
        """모킹된 클라이언트"""
        with patch("opensearch_client.client.OpenSearch") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            client = OpenSearchClient()
            yield client, mock_instance

    def test_hybrid_search(self, client):
        """하이브리드 검색 실행"""
        os_client, mock_instance = client
        mock_instance.search.return_value = {"hits": {"hits": []}}

        result = os_client.hybrid_search(
            index_name="test-index",
            query="test query",
            query_vector=[0.1] * 384,
            pipeline="my-pipeline",
            text_fields=["content"],
            vector_field="embedding",
        )

        mock_instance.search.assert_called_once()
        call_kwargs = mock_instance.search.call_args[1]
        assert call_kwargs["index"] == "test-index"
        assert call_kwargs["params"] == {"search_pipeline": "my-pipeline"}
        assert result == {"hits": {"hits": []}}

    def test_hybrid_search_with_all_params(self, client):
        """모든 파라미터와 함께 하이브리드 검색"""
        os_client, mock_instance = client
        mock_instance.search.return_value = {"hits": {"hits": []}}

        os_client.hybrid_search(
            index_name="test-index",
            query="test query",
            query_vector=[0.1] * 384,
            pipeline="my-pipeline",
            text_fields=["title", "content"],
            vector_field="embedding",
            k=5,
            size=10,
            text_boost=2.0,
            vector_boost=0.5,
            filter={"term": {"category": "tech"}},
            source=["title", "content"],
            min_score=0.5,
        )

        mock_instance.search.assert_called_once()

    def test_setup_hybrid_pipeline_default(self, client):
        """기본 하이브리드 파이프라인 설정"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"acknowledged": True}

        result = os_client.setup_hybrid_pipeline()

        mock_instance.transport.perform_request.assert_called_once()
        call_args = mock_instance.transport.perform_request.call_args
        assert call_args[0][0] == "PUT"
        assert "hybrid-pipeline" in call_args[0][1]
        assert result == {"acknowledged": True}

    def test_setup_hybrid_pipeline_custom(self, client):
        """커스텀 하이브리드 파이프라인 설정"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"acknowledged": True}

        os_client.setup_hybrid_pipeline(
            pipeline_id="custom-pipeline",
            text_weight=0.5,
            vector_weight=0.5,
        )

        call_args = mock_instance.transport.perform_request.call_args
        assert "custom-pipeline" in call_args[0][1]

    def test_setup_hybrid_pipeline_with_rrf(self, client):
        """RRF 사용 하이브리드 파이프라인"""
        os_client, mock_instance = client
        mock_instance.transport.perform_request.return_value = {"acknowledged": True}

        os_client.setup_hybrid_pipeline(pipeline_id="rrf-pipeline", use_rrf=True)

        mock_instance.transport.perform_request.assert_called_once()
        call_args = mock_instance.transport.perform_request.call_args
        assert "rrf-pipeline" in call_args[0][1]
