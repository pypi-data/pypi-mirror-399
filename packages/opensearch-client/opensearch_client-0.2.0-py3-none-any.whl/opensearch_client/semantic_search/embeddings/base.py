"""
임베딩 기본 인터페이스

다양한 임베딩 모델을 위한 추상 클래스
"""

from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    """
    임베딩 모델 기본 인터페이스

    모든 임베딩 구현체는 이 클래스를 상속해야 합니다.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """벡터 차원 반환"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """모델 이름 반환"""
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """
        단일 텍스트를 벡터로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            벡터 (float 리스트)
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        여러 텍스트를 벡터로 변환

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            벡터 리스트
        """
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(model={self.model_name}, dim={self.dimension})"
        )
