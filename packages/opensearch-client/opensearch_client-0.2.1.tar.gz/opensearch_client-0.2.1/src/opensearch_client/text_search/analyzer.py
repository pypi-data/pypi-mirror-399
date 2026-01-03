"""
분석기 설정 모듈

한국어 (Nori), 영어 등 다양한 언어 분석기 설정 제공
"""

from enum import Enum
from typing import Any


class DecompoundMode(str, Enum):
    """Nori 토크나이저 복합어 분해 모드"""

    NONE = "none"  # 복합어 분해 안함
    DISCARD = "discard"  # 복합어만 버리고 분해된 토큰만 유지
    MIXED = "mixed"  # 복합어와 분해된 토큰 모두 유지


class AnalyzerConfig:
    """
    OpenSearch 분석기 설정 클래스

    다양한 언어에 대한 분석기 설정을 제공합니다.
    """

    @staticmethod
    def korean_analyzer(
        name: str = "korean",
        decompound_mode: DecompoundMode = DecompoundMode.MIXED,
        user_dictionary: str | None = None,
        stoptags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        한국어 (Nori) 분석기 설정

        Args:
            name: 분석기 이름
            decompound_mode: 복합어 분해 모드
            user_dictionary: 사용자 정의 사전 경로
            stoptags: 제외할 품사 태그 목록

        Returns:
            분석기 설정
        """
        # 기본 토크나이저 설정
        tokenizer_config: dict[str, Any] = {
            "type": "nori_tokenizer",
            "decompound_mode": decompound_mode.value,
        }

        if user_dictionary:
            tokenizer_config["user_dictionary"] = user_dictionary

        # 기본 필터
        filters = ["lowercase", "nori_readingform"]

        # 품사 필터 추가
        if stoptags:
            filters.append("nori_stoptags")

        return {
            "analysis": {
                "tokenizer": {f"{name}_tokenizer": tokenizer_config},
                "filter": {
                    "nori_stoptags": {
                        "type": "nori_part_of_speech",
                        "stoptags": stoptags
                        or [
                            "E",  # 어미
                            "IC",  # 감탄사
                            "J",  # 조사
                            "MAG",  # 일반 부사
                            "MAJ",  # 접속 부사
                            "MM",  # 관형사
                            "SP",  # 공백
                            "SSC",  # 닫는 괄호
                            "SSO",  # 여는 괄호
                            "SC",  # 구분자
                            "SE",  # 생략부호
                            "XPN",  # 접두사
                            "XSA",  # 형용사 파생 접미사
                            "XSN",  # 명사 파생 접미사
                            "XSV",  # 동사 파생 접미사
                            "UNA",  # 분석 불가
                            "NA",  # 분석 불가
                            "VSV",  # 분석 불가
                        ],
                    }
                },
                "analyzer": {
                    name: {
                        "type": "custom",
                        "tokenizer": f"{name}_tokenizer",
                        "filter": filters,
                    }
                },
            }
        }

    @staticmethod
    def standard_analyzer(name: str = "standard_custom") -> dict[str, Any]:
        """
        표준 분석기 설정 (영어 등)

        Args:
            name: 분석기 이름

        Returns:
            분석기 설정
        """
        return {
            "analysis": {
                "analyzer": {
                    name: {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            }
        }

    @staticmethod
    def whitespace_analyzer(name: str = "whitespace_custom") -> dict[str, Any]:
        """
        공백 기반 분석기 설정

        Args:
            name: 분석기 이름

        Returns:
            분석기 설정
        """
        return {
            "analysis": {
                "analyzer": {
                    name: {
                        "type": "custom",
                        "tokenizer": "whitespace",
                        "filter": ["lowercase"],
                    }
                }
            }
        }

    @staticmethod
    def ngram_analyzer(
        name: str = "ngram_analyzer", min_gram: int = 2, max_gram: int = 3
    ) -> dict[str, Any]:
        """
        N-gram 분석기 설정

        부분 문자열 매칭에 유용

        Args:
            name: 분석기 이름
            min_gram: 최소 gram 크기
            max_gram: 최대 gram 크기

        Returns:
            분석기 설정
        """
        return {
            "analysis": {
                "tokenizer": {
                    f"{name}_tokenizer": {
                        "type": "ngram",
                        "min_gram": min_gram,
                        "max_gram": max_gram,
                        "token_chars": ["letter", "digit"],
                    }
                },
                "analyzer": {
                    name: {
                        "type": "custom",
                        "tokenizer": f"{name}_tokenizer",
                        "filter": ["lowercase"],
                    }
                },
            }
        }

    @classmethod
    def merge_settings(cls, *settings: dict[str, Any]) -> dict[str, Any]:
        """
        여러 분석기 설정을 병합

        Args:
            *settings: 병합할 설정들

        Returns:
            병합된 설정
        """
        merged: dict[str, Any] = {"analysis": {}}

        for setting in settings:
            if "analysis" not in setting:
                continue

            analysis = setting["analysis"]

            for key in ["tokenizer", "filter", "analyzer", "char_filter"]:
                if key in analysis:
                    if key not in merged["analysis"]:
                        merged["analysis"][key] = {}
                    merged["analysis"][key].update(analysis[key])

        return merged
