"""
OpenSearchClient 통합 테스트

OpenSearch 연결이 필요합니다.
docker-compose.test.yml로 테스트 환경을 시작하세요.
"""

import pytest


@pytest.mark.integration
class TestOpenSearchClient:
    """OpenSearchClient 통합 테스트"""

    def test_ping(self, opensearch_client):
        """OpenSearch 연결 확인"""
        assert opensearch_client.ping() is True

    def test_info(self, opensearch_client):
        """클러스터 정보 조회"""
        info = opensearch_client.info()
        assert "version" in info
        assert "cluster_name" in info

    def test_create_and_delete_index(self, opensearch_client, test_index_name):
        """인덱스 생성 및 삭제"""
        index_name = f"{test_index_name}-basic"

        # 기존 인덱스 삭제 (있는 경우)
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)

        # 인덱스 생성
        result = opensearch_client.create_index(index_name)
        assert result.get("acknowledged") is True
        assert opensearch_client.index_exists(index_name) is True

        # 인덱스 삭제
        result = opensearch_client.delete_index(index_name)
        assert result.get("acknowledged") is True
        assert opensearch_client.index_exists(index_name) is False

    def test_index_and_get_document(self, opensearch_client, test_index_name):
        """문서 인덱싱 및 조회"""
        index_name = f"{test_index_name}-doc"

        # 인덱스 생성
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)
        opensearch_client.create_index(index_name)

        try:
            # 문서 인덱싱
            doc = {"title": "테스트 문서", "content": "내용입니다"}
            result = opensearch_client.index_document(index_name, doc, doc_id="test-1")
            assert result.get("result") in ["created", "updated"]

            # 문서 조회
            opensearch_client.refresh(index_name)
            doc = opensearch_client.get_document(index_name, "test-1")
            assert doc["_source"]["title"] == "테스트 문서"

        finally:
            opensearch_client.delete_index(index_name)

    def test_bulk_index(self, opensearch_client, test_index_name, sample_documents):
        """벌크 인덱싱"""
        index_name = f"{test_index_name}-bulk"

        # 인덱스 생성
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)
        opensearch_client.create_index(index_name)

        try:
            # 벌크 인덱싱
            result = opensearch_client.bulk_index(index_name, sample_documents)
            assert result.get("errors") is False

            # 문서 수 확인
            opensearch_client.refresh(index_name)
            search_result = opensearch_client.search(
                index_name, {"query": {"match_all": {}}}
            )
            assert search_result["hits"]["total"]["value"] == len(sample_documents)

        finally:
            opensearch_client.delete_index(index_name)

    def test_search(self, opensearch_client, test_index_name, sample_documents):
        """검색 테스트"""
        index_name = f"{test_index_name}-search"

        # 인덱스 생성
        if opensearch_client.index_exists(index_name):
            opensearch_client.delete_index(index_name)
        opensearch_client.create_index(index_name)

        try:
            # 문서 인덱싱
            opensearch_client.bulk_index(index_name, sample_documents)
            opensearch_client.refresh(index_name)

            # 검색
            result = opensearch_client.search(
                index_name, {"query": {"match": {"text": "프로그래밍"}}}
            )

            assert result["hits"]["total"]["value"] >= 1

        finally:
            opensearch_client.delete_index(index_name)
