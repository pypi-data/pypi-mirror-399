"""
FastEmbed 임베딩 구현

로컬에서 실행되는 빠른 임베딩 모델
"""

from typing import ClassVar

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding


class FastEmbedEmbedding(BaseEmbedding):
    """
    FastEmbed 기반 임베딩

    로컬에서 실행되며 sentence-transformers보다 빠릅니다.

    사용 가능한 모델:
    - BAAI/bge-small-en-v1.5 (384 dim, 영어)
    - BAAI/bge-base-en-v1.5 (768 dim, 영어)
    - intfloat/multilingual-e5-small (384 dim, 다국어)
    - intfloat/multilingual-e5-base (768 dim, 다국어)
    """

    DEFAULT_MODEL: ClassVar[str] = "BAAI/bge-small-en-v1.5"
    MODEL_DIMENSIONS: ClassVar[dict[str, int]] = {
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
        "BAAI/bge-large-en-v1.5": 1024,
        "intfloat/multilingual-e5-small": 384,
        "intfloat/multilingual-e5-base": 768,
        "intfloat/e5-small-v2": 384,
        "intfloat/e5-base-v2": 768,
    }

    def __init__(
        self,
        model_name: str | None = None,
        cache_dir: str | None = None,
        threads: int | None = None,
    ):
        """
        FastEmbed 임베딩 초기화

        Args:
            model_name: 사용할 모델 이름 (기본: BAAI/bge-small-en-v1.5)
            cache_dir: 모델 캐시 디렉토리
            threads: 사용할 스레드 수

        Raises:
            ImportError: fastembed가 설치되지 않은 경우
        """
        try:
            from fastembed import TextEmbedding
        except ImportError as err:
            raise ImportError(
                "fastembed is not installed. "
                "Install it with: uv add opensearch-client[local]"
            ) from err

        self._model_name = model_name or self.DEFAULT_MODEL
        self._dimension = self.MODEL_DIMENSIONS.get(self._model_name, 384)

        # FastEmbed 모델 초기화
        kwargs = {}
        if cache_dir:
            kwargs["cache_dir"] = cache_dir
        if threads:
            kwargs["threads"] = threads

        self._model = TextEmbedding(model_name=self._model_name, **kwargs)

    @property
    def dimension(self) -> int:
        return self._dimension

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
        embeddings = list(self._model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        배치 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            벡터 리스트
        """
        embeddings = list(self._model.embed(texts))
        return [emb.tolist() for emb in embeddings]
