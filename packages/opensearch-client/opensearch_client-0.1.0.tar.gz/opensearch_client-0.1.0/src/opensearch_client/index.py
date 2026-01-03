"""
인덱스 관리 모듈

텍스트, 벡터, 하이브리드 인덱스 생성 및 관리
"""

from typing import Any


class IndexManager:
    """
    OpenSearch 인덱스 관리 클래스

    텍스트 검색, 벡터 검색, 하이브리드 검색을 위한 인덱스 설정 제공
    """

    @staticmethod
    def get_korean_analyzer_settings() -> dict[str, Any]:
        """
        한국어 (Nori) 분석기 설정 반환

        Returns:
            Nori 토크나이저 및 필터 설정
        """
        return {
            "analysis": {
                "analyzer": {
                    "korean": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": ["nori_part_of_speech"],
                    },
                    "korean_search": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": ["nori_readingform"],
                    },
                },
                "tokenizer": {
                    "nori_tokenizer": {
                        "type": "nori_tokenizer",
                        "decompound_mode": "mixed",
                    }
                },
            }
        }

    @staticmethod
    def get_text_index_mapping(
        text_fields: dict[str, str] | None = None, analyzer: str = "korean"
    ) -> dict[str, Any]:
        """
        텍스트 검색용 인덱스 매핑 생성

        Args:
            text_fields: 텍스트 필드명과 타입 매핑 (기본: question, answer)
            analyzer: 사용할 분석기 (기본: korean)

        Returns:
            인덱스 매핑 설정
        """
        if text_fields is None:
            text_fields = {"title": "text", "question": "text", "answer": "text"}

        properties = {}
        for field_name, field_type in text_fields.items():
            if field_type == "text":
                properties[field_name] = {"type": "text", "analyzer": analyzer}
            else:
                properties[field_name] = {"type": field_type}

        # 기본 메타데이터 필드 추가
        properties.update(
            {
                "source_id": {"type": "keyword"},
                "source_path": {"type": "keyword"},
                "file_type": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        )

        return {"properties": properties}

    @staticmethod
    def get_knn_index_settings(ef_search: int = 100) -> dict[str, Any]:
        """
        k-NN 벡터 인덱스 설정 반환

        Args:
            ef_search: 검색 시 탐색할 후보 수 (높을수록 정확도 증가, 속도 감소)

        Returns:
            k-NN 인덱스 설정
        """
        return {"index": {"knn": True, "knn.algo_param.ef_search": ef_search}}

    @staticmethod
    def get_knn_field_mapping(
        field_name: str = "vector",
        dimension: int = 1536,
        space_type: str = "cosinesimil",
        engine: str = "lucene",
        ef_construction: int = 128,
        m: int = 16,
    ) -> dict[str, Any]:
        """
        k-NN 벡터 필드 매핑 생성

        Args:
            field_name: 벡터 필드명
            dimension: 벡터 차원
            space_type: 유사도 측정 방법
            engine: k-NN 엔진
            ef_construction: HNSW 그래프 구축 파라미터
            m: HNSW 연결 수

        Returns:
            벡터 필드 매핑
        """
        return {
            field_name: {
                "type": "knn_vector",
                "dimension": dimension,
                "method": {
                    "name": "hnsw",
                    "space_type": space_type,
                    "engine": engine,
                    "parameters": {"ef_construction": ef_construction, "m": m},
                },
            }
        }

    @classmethod
    def create_hybrid_index_body(
        cls,
        vector_dimension: int = 1536,
        text_analyzer: str = "korean",
        text_fields: dict[str, str] | None = None,
        vector_field: str = "vector",
        space_type: str = "cosinesimil",
        use_korean_analyzer: bool = True,
    ) -> dict[str, Any]:
        """
        하이브리드 검색용 인덱스 설정 생성

        텍스트 검색 + 벡터 검색을 위한 통합 인덱스

        Args:
            vector_dimension: 벡터 차원
            text_analyzer: 텍스트 분석기
            text_fields: 텍스트 필드 설정
            vector_field: 벡터 필드명
            space_type: 벡터 유사도 측정 방법
            use_korean_analyzer: 한국어 분석기 사용 여부

        Returns:
            통합 인덱스 설정 (settings + mappings)
        """
        # 설정 병합
        if use_korean_analyzer:
            settings = {
                **cls.get_korean_analyzer_settings(),
                **cls.get_knn_index_settings(),
            }
        else:
            settings = cls.get_knn_index_settings()

        # 매핑 병합
        text_mapping = cls.get_text_index_mapping(text_fields, text_analyzer)
        vector_mapping = cls.get_knn_field_mapping(
            vector_field, vector_dimension, space_type
        )
        text_mapping["properties"].update(vector_mapping)

        return {"settings": settings, "mappings": text_mapping}

    @classmethod
    def create_text_index_body(
        cls,
        text_field: str = "content",
        use_korean_analyzer: bool = True,
        additional_fields: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        텍스트 검색용 인덱스 설정 생성

        Args:
            text_field: 메인 텍스트 필드명
            use_korean_analyzer: 한국어 분석기 사용 여부
            additional_fields: 추가 필드 설정

        Returns:
            인덱스 설정 (settings + mappings)
        """
        text_fields = {text_field: "text"}
        if additional_fields:
            text_fields.update(additional_fields)

        analyzer = "korean" if use_korean_analyzer else "standard"

        settings = cls.get_korean_analyzer_settings() if use_korean_analyzer else {}

        return {
            "settings": settings,
            "mappings": cls.get_text_index_mapping(text_fields, analyzer),
        }

    @classmethod
    def create_vector_index_body(
        cls,
        vector_field: str = "vector",
        vector_dimension: int = 1536,
        space_type: str = "cosinesimil",
    ) -> dict[str, Any]:
        """
        벡터 검색용 인덱스 설정 생성

        Args:
            vector_field: 벡터 필드명
            vector_dimension: 벡터 차원
            space_type: 유사도 측정 방법

        Returns:
            인덱스 설정 (settings + mappings)
        """
        settings = cls.get_knn_index_settings()
        vector_mapping = cls.get_knn_field_mapping(
            vector_field, vector_dimension, space_type
        )

        return {
            "settings": settings,
            "mappings": {"properties": {"text": {"type": "text"}, **vector_mapping}},
        }
