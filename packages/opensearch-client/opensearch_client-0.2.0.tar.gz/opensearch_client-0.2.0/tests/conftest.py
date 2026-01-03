"""
pytest 설정 및 공통 fixture

단위 테스트와 통합 테스트를 위한 설정
"""

import os

import pytest

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding


class MockEmbedder(BaseEmbedding):
    """
    테스트용 Mock 임베더

    실제 임베딩 모델 없이 테스트하기 위한 클래스
    """

    def __init__(self, dim: int = 384):
        self._dimension = dim

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        """고정된 벡터 반환"""
        return [0.1] * self._dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """각 텍스트에 대해 고정된 벡터 반환"""
        return [[0.1] * self._dimension for _ in texts]


# 통합 테스트용 OpenSearch 설정
OPENSEARCH_TEST_HOST = os.getenv("OPENSEARCH_TEST_HOST", "localhost")
OPENSEARCH_TEST_PORT = int(os.getenv("OPENSEARCH_TEST_PORT", "9201"))


def pytest_configure(config):
    """pytest 마커 등록"""
    config.addinivalue_line("markers", "integration: 통합 테스트 (OpenSearch 필요)")
    config.addinivalue_line("markers", "e2e: E2E 테스트 (전체 파이프라인)")


@pytest.fixture
def mock_embedder():
    """테스트용 Mock 임베더 (384차원)"""
    return MockEmbedder(dim=384)


@pytest.fixture
def mock_embedder_1536():
    """테스트용 Mock 임베더 (1536차원, OpenAI 호환)"""
    return MockEmbedder(dim=1536)


@pytest.fixture
def sample_vector():
    """테스트용 샘플 벡터 (384차원)"""
    return [0.1] * 384


@pytest.fixture
def sample_vector_1536():
    """테스트용 샘플 벡터 (1536차원, OpenAI)"""
    return [0.05] * 1536


@pytest.fixture
def sample_documents():
    """테스트용 샘플 문서"""
    return [
        {"text": "빵은 밀가루로 만든 음식입니다", "category": "food"},
        {"text": "파이썬은 프로그래밍 언어입니다", "category": "tech"},
        {"text": "OpenSearch는 검색 엔진입니다", "category": "tech"},
    ]


@pytest.fixture(scope="module")
def opensearch_client():
    """
    통합 테스트용 OpenSearch 클라이언트

    테스트 환경의 OpenSearch에 연결
    """
    from opensearch_client import OpenSearchClient

    client = OpenSearchClient(
        host=OPENSEARCH_TEST_HOST, port=OPENSEARCH_TEST_PORT, use_ssl=False
    )

    # 연결 확인
    if not client.ping():
        pytest.skip("OpenSearch not available")

    yield client


@pytest.fixture
def test_index_name():
    """테스트용 인덱스 이름"""
    return "test-opensearch-client"


@pytest.fixture
def hybrid_test_index(opensearch_client, test_index_name):
    """
    하이브리드 검색 테스트용 인덱스 생성/삭제

    테스트 후 자동으로 인덱스 삭제
    """
    from opensearch_client import IndexManager

    index_name = f"{test_index_name}-hybrid"

    # 기존 인덱스 삭제
    if opensearch_client.index_exists(index_name):
        opensearch_client.delete_index(index_name)

    # 하이브리드 인덱스 생성
    body = IndexManager.create_hybrid_index_body(
        text_fields={"text": "text"},
        vector_field="vector",
        vector_dimension=384,
        use_korean_analyzer=False,
    )
    opensearch_client.create_index(index_name, body)

    yield index_name

    # 테스트 후 인덱스 삭제
    if opensearch_client.index_exists(index_name):
        opensearch_client.delete_index(index_name)
