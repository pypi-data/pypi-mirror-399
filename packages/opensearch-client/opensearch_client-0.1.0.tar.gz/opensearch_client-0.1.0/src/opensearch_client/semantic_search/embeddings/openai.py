"""
OpenAI 임베딩 구현

OpenAI API를 사용한 임베딩
"""

from typing import ClassVar

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    """
    OpenAI API 기반 임베딩

    사용 가능한 모델:
    - text-embedding-3-small (1536 dim)
    - text-embedding-3-large (3072 dim)
    - text-embedding-ada-002 (1536 dim, legacy)
    """

    DEFAULT_MODEL: ClassVar[str] = "text-embedding-3-small"
    MODEL_DIMENSIONS: ClassVar[dict[str, int]] = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        dimensions: int | None = None,
    ):
        """
        OpenAI 임베딩 초기화

        Args:
            api_key: OpenAI API 키 (없으면 OPENAI_API_KEY 환경 변수 사용)
            model_name: 사용할 모델 이름 (기본: text-embedding-3-small)
            dimensions: 출력 차원 수 (text-embedding-3-* 모델에서 지원)

        Raises:
            ImportError: openai가 설치되지 않은 경우
        """
        try:
            from openai import OpenAI
        except ImportError as err:
            raise ImportError(
                "openai is not installed. "
                "Install it with: uv add opensearch-client[openai]"
            ) from err

        self._model_name = model_name or self.DEFAULT_MODEL
        self._dimensions = dimensions
        self._default_dimension = self.MODEL_DIMENSIONS.get(self._model_name, 1536)

        # OpenAI 클라이언트 초기화
        self._client = OpenAI(api_key=api_key)

    @property
    def dimension(self) -> int:
        return self._dimensions or self._default_dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed(self, text: str) -> list[float]:
        """
        단일 텍스트 임베딩

        Args:
            text: 임베딩할 텍스트

        Returns:
            벡터 (float 리스트)
        """
        # text-embedding-3-* 모델은 dimensions 파라미터 지원
        if self._dimensions and self._model_name.startswith("text-embedding-3"):
            response = self._client.embeddings.create(
                input=text, model=self._model_name, dimensions=self._dimensions
            )
        else:
            response = self._client.embeddings.create(
                input=text, model=self._model_name
            )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        배치 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            벡터 리스트
        """
        # text-embedding-3-* 모델은 dimensions 파라미터 지원
        if self._dimensions and self._model_name.startswith("text-embedding-3"):
            response = self._client.embeddings.create(
                input=texts, model=self._model_name, dimensions=self._dimensions
            )
        else:
            response = self._client.embeddings.create(
                input=texts, model=self._model_name
            )

        # 인덱스 순서대로 정렬
        sorted_embeddings = sorted(response.data, key=lambda x: x.index)
        return [emb.embedding for emb in sorted_embeddings]
