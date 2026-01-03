"""
Search Pipeline 관리 모듈

OpenSearch 2.10+ Search Pipeline 설정 및 관리
"""

from enum import Enum
from typing import Any


class NormalizationType(str, Enum):
    """점수 정규화 방법"""

    MIN_MAX = "min_max"
    L2 = "l2"


class CombinationType(str, Enum):
    """점수 결합 방법"""

    ARITHMETIC_MEAN = "arithmetic_mean"
    GEOMETRIC_MEAN = "geometric_mean"
    HARMONIC_MEAN = "harmonic_mean"


class SearchPipelineManager:
    """
    Search Pipeline 관리 클래스

    하이브리드 검색을 위한 Search Pipeline 생성 및 관리
    OpenSearch 2.10+ 필요
    """

    @staticmethod
    def create_normalization_processor(
        normalization_technique: NormalizationType = NormalizationType.MIN_MAX,
        combination_technique: CombinationType = CombinationType.ARITHMETIC_MEAN,
        weights: list[float] | None = None,
    ) -> dict[str, Any]:
        """
        Normalization Processor 설정 생성

        Args:
            normalization_technique: 점수 정규화 방법 (min_max 또는 l2)
            combination_technique: 점수 결합 방법
            weights: 각 쿼리의 가중치 리스트 (예: [0.3, 0.7])

        Returns:
            Normalization Processor 설정 딕셔너리
        """
        processor: dict[str, Any] = {
            "normalization-processor": {
                "normalization": {"technique": normalization_technique.value},
                "combination": {"technique": combination_technique.value},
            }
        }

        if weights:
            processor["normalization-processor"]["combination"]["parameters"] = {
                "weights": weights
            }

        return processor

    @staticmethod
    def create_rrf_processor(
        rank_constant: int = 60, window_size: int = 100
    ) -> dict[str, Any]:
        """
        RRF (Reciprocal Rank Fusion) Processor 설정 생성

        OpenSearch 2.19+ 필요

        Args:
            rank_constant: RRF 공식의 k 값 (기본: 60)
            window_size: 결합할 상위 결과 수 (기본: 100)

        Returns:
            Score Ranker Processor 설정 딕셔너리
        """
        return {
            "score-ranker-processor": {
                "combination": {
                    "technique": "rrf",
                    "parameters": {
                        "rank_constant": rank_constant,
                        "window_size": window_size,
                    },
                }
            }
        }

    @classmethod
    def build_pipeline_body(
        cls,
        description: str = "Hybrid search pipeline",
        use_rrf: bool = False,
        normalization_technique: NormalizationType = NormalizationType.MIN_MAX,
        combination_technique: CombinationType = CombinationType.ARITHMETIC_MEAN,
        weights: list[float] | None = None,
        rank_constant: int = 60,
        window_size: int = 100,
    ) -> dict[str, Any]:
        """
        Search Pipeline 본문 생성

        Args:
            description: 파이프라인 설명
            use_rrf: RRF 사용 여부 (True면 RRF, False면 normalization)
            normalization_technique: 정규화 방법 (use_rrf=False일 때)
            combination_technique: 결합 방법 (use_rrf=False일 때)
            weights: 가중치 리스트 (use_rrf=False일 때)
            rank_constant: RRF k 값 (use_rrf=True일 때)
            window_size: RRF 윈도우 크기 (use_rrf=True일 때)

        Returns:
            Search Pipeline 설정 딕셔너리
        """
        if use_rrf:
            phase_results_processor = cls.create_rrf_processor(
                rank_constant=rank_constant, window_size=window_size
            )
        else:
            phase_results_processor = cls.create_normalization_processor(
                normalization_technique=normalization_technique,
                combination_technique=combination_technique,
                weights=weights,
            )

        return {
            "description": description,
            "phase_results_processors": [phase_results_processor],
        }

    @staticmethod
    def build_default_hybrid_pipeline(
        text_weight: float = 0.3, vector_weight: float = 0.7
    ) -> dict[str, Any]:
        """
        기본 하이브리드 검색 파이프라인 생성

        Args:
            text_weight: 텍스트 검색 가중치
            vector_weight: 벡터 검색 가중치

        Returns:
            Search Pipeline 설정 딕셔너리
        """
        return {
            "description": "Default hybrid search pipeline with weighted combination",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {"weights": [text_weight, vector_weight]},
                        },
                    }
                }
            ],
        }
