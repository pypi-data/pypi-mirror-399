"""
하이브리드 검색 통합 테스트

OpenSearch 연결이 필요합니다.
docker-compose.test.yml로 테스트 환경을 시작하세요.
"""

import contextlib

import pytest

from opensearch_client import IndexManager


@pytest.mark.integration
class TestHybridSearch:
    """하이브리드 검색 통합 테스트"""

    @pytest.fixture
    def hybrid_index(self, opensearch_client, test_index_name, sample_vector):
        """하이브리드 인덱스 생성/삭제"""
        index_name = f"{test_index_name}-hybrid-search"

        # 기존 인덱스 삭제
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)

        # 하이브리드 인덱스 생성 (Nori 한국어 분석기 사용)
        body = IndexManager.create_hybrid_index_body(
            vector_dimension=384,  # sample_vector와 동일
            text_fields={"text": "text"},
            vector_field="vector",
        )
        opensearch_client.create_index(index_name, body)

        yield index_name

        # 정리
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)

    @pytest.fixture
    def hybrid_pipeline(self, opensearch_client):
        """테스트용 Search Pipeline 생성/삭제"""
        pipeline_id = "test-hybrid-pipeline"

        # 기존 파이프라인 삭제 시도
        with contextlib.suppress(Exception):
            opensearch_client.delete_search_pipeline(pipeline_id)

        # 파이프라인 생성
        opensearch_client.setup_hybrid_pipeline(
            pipeline_id=pipeline_id, text_weight=0.3, vector_weight=0.7
        )

        yield pipeline_id

        # 정리
        with contextlib.suppress(Exception):
            opensearch_client.delete_search_pipeline(pipeline_id)

    def test_create_hybrid_index(self, opensearch_client, hybrid_index):
        """하이브리드 인덱스 생성 확인"""
        assert opensearch_client.index_exists(hybrid_index) is True

        # 매핑 확인
        mapping = opensearch_client.raw_client.indices.get_mapping(index=hybrid_index)
        properties = mapping[hybrid_index]["mappings"]["properties"]

        assert "text" in properties
        assert "vector" in properties
        assert properties["vector"]["type"] == "knn_vector"

    def test_index_hybrid_document(
        self, opensearch_client, hybrid_index, sample_vector
    ):
        """하이브리드 문서 인덱싱"""
        doc = {"text": "OpenSearch는 검색 엔진입니다", "vector": sample_vector}

        result = opensearch_client.index_document(hybrid_index, doc, doc_id="test-1")
        assert result.get("result") in ["created", "updated"]

        # 문서 확인
        opensearch_client.refresh(hybrid_index)
        retrieved = opensearch_client.get_document(hybrid_index, "test-1")
        assert retrieved["_source"]["text"] == doc["text"]
        assert len(retrieved["_source"]["vector"]) == 384

    def test_setup_hybrid_pipeline(self, opensearch_client, hybrid_pipeline):
        """하이브리드 파이프라인 설정"""
        # 파이프라인 조회
        pipeline = opensearch_client.get_search_pipeline(hybrid_pipeline)
        assert hybrid_pipeline in pipeline

    def test_knn_search(self, opensearch_client, hybrid_index, sample_vector):
        """k-NN 검색 테스트"""
        # 문서 인덱싱
        docs = [
            {"text": "첫 번째 문서", "vector": sample_vector},
            {"text": "두 번째 문서", "vector": [0.2] * 384},
        ]

        for i, doc in enumerate(docs):
            opensearch_client.index_document(hybrid_index, doc, doc_id=f"doc-{i}")

        opensearch_client.refresh(hybrid_index)

        # k-NN 검색
        from opensearch_client.semantic_search.knn_search import KNNSearch

        query = KNNSearch.knn_query(field="vector", vector=sample_vector, k=2)
        body = KNNSearch.build_search_body(query, size=10)

        result = opensearch_client.search(hybrid_index, body)
        hits = result["hits"]["hits"]

        # sample_vector와 동일한 벡터를 가진 문서가 상위에 있어야 함
        assert len(hits) >= 1
        assert hits[0]["_source"]["text"] == "첫 번째 문서"
