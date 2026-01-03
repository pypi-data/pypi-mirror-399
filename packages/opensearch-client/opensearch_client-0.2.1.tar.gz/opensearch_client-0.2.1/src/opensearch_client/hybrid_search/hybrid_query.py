"""
하이브리드 쿼리 빌더 모듈

텍스트 쿼리와 벡터 쿼리를 결합한 하이브리드 검색 쿼리 생성
"""

from typing import Any

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding


class HybridQueryBuilder:
    """
    하이브리드 검색 쿼리 빌더

    텍스트 검색과 벡터 검색을 결합한 쿼리 생성
    """

    @staticmethod
    def build_text_query(
        query: str, fields: list[str] | None = None, boost: float = 1.0
    ) -> dict[str, Any]:
        """
        텍스트 검색 쿼리 생성

        Args:
            query: 검색 쿼리
            fields: 검색 필드 목록 (기본: ["text"])
            boost: 쿼리 가중치

        Returns:
            텍스트 쿼리 DSL
        """
        search_fields = fields or ["text"]

        return {
            "multi_match": {"query": query, "fields": search_fields, "boost": boost}
        }

    @staticmethod
    def build_knn_query(
        vector: list[float], field: str = "vector", k: int = 10, boost: float = 1.0
    ) -> dict[str, Any]:
        """
        k-NN 벡터 검색 쿼리 생성

        Args:
            vector: 쿼리 벡터
            field: 벡터 필드명
            k: 반환할 최근접 이웃 수
            boost: 쿼리 가중치

        Returns:
            k-NN 쿼리 DSL
        """
        return {"knn": {field: {"vector": vector, "k": k, "boost": boost}}}

    @classmethod
    def build_hybrid_query(
        cls,
        text_query: str,
        query_vector: list[float],
        text_fields: list[str] | None = None,
        vector_field: str = "vector",
        k: int = 10,
        text_boost: float = 1.0,
        vector_boost: float = 1.0,
        filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        하이브리드 검색 쿼리 생성

        텍스트 쿼리와 k-NN 쿼리를 bool 쿼리의 should 절로 결합

        Args:
            text_query: 텍스트 검색 쿼리
            query_vector: 쿼리 벡터
            text_fields: 텍스트 검색 필드 목록
            vector_field: 벡터 필드명
            k: k-NN 결과 수
            text_boost: 텍스트 쿼리 boost
            vector_boost: 벡터 쿼리 boost
            filter: 필터 조건

        Returns:
            하이브리드 쿼리 DSL
        """
        text_q = cls.build_text_query(text_query, text_fields, text_boost)
        knn_q = cls.build_knn_query(query_vector, vector_field, k, vector_boost)

        hybrid_query: dict[str, Any] = {"hybrid": {"queries": [text_q, knn_q]}}

        if filter:
            hybrid_query["hybrid"]["filter"] = filter

        return hybrid_query

    @classmethod
    def build_hybrid_query_with_embedding(
        cls,
        text_query: str,
        embedder: BaseEmbedding,
        text_fields: list[str] | None = None,
        vector_field: str = "vector",
        k: int = 10,
        text_boost: float = 1.0,
        vector_boost: float = 1.0,
        filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        임베딩 모델을 사용한 하이브리드 검색 쿼리 생성

        Args:
            text_query: 텍스트 검색 쿼리
            embedder: 임베딩 모델 인스턴스
            text_fields: 텍스트 검색 필드 목록
            vector_field: 벡터 필드명
            k: k-NN 결과 수
            text_boost: 텍스트 쿼리 boost
            vector_boost: 벡터 쿼리 boost
            filter: 필터 조건

        Returns:
            하이브리드 쿼리 DSL
        """
        query_vector = embedder.embed(text_query)

        return cls.build_hybrid_query(
            text_query=text_query,
            query_vector=query_vector,
            text_fields=text_fields,
            vector_field=vector_field,
            k=k,
            text_boost=text_boost,
            vector_boost=vector_boost,
            filter=filter,
        )

    @staticmethod
    def build_search_body(
        query: dict[str, Any],
        size: int = 10,
        source: list[str] | None = None,
        min_score: float | None = None,
        search_pipeline: str | None = None,
    ) -> dict[str, Any]:
        """
        검색 요청 본문 생성

        Args:
            query: 쿼리 DSL
            size: 반환할 결과 수
            source: 반환할 필드 목록
            min_score: 최소 점수 임계값
            search_pipeline: 사용할 Search Pipeline 이름

        Returns:
            검색 요청 본문
        """
        body: dict[str, Any] = {"query": query, "size": size}

        if source:
            body["_source"] = source
        if min_score is not None:
            body["min_score"] = min_score

        return body

    @classmethod
    def build_complete_hybrid_search(
        cls,
        text_query: str,
        query_vector: list[float],
        text_fields: list[str] | None = None,
        vector_field: str = "vector",
        k: int = 10,
        size: int = 10,
        text_boost: float = 1.0,
        vector_boost: float = 1.0,
        filter: dict[str, Any] | None = None,
        source: list[str] | None = None,
        min_score: float | None = None,
    ) -> dict[str, Any]:
        """
        완전한 하이브리드 검색 요청 본문 생성

        Args:
            text_query: 텍스트 검색 쿼리
            query_vector: 쿼리 벡터
            text_fields: 텍스트 검색 필드 목록
            vector_field: 벡터 필드명
            k: k-NN 결과 수
            size: 반환할 결과 수
            text_boost: 텍스트 쿼리 boost
            vector_boost: 벡터 쿼리 boost
            filter: 필터 조건
            source: 반환할 필드 목록
            min_score: 최소 점수 임계값

        Returns:
            완전한 검색 요청 본문
        """
        query = cls.build_hybrid_query(
            text_query=text_query,
            query_vector=query_vector,
            text_fields=text_fields,
            vector_field=vector_field,
            k=k,
            text_boost=text_boost,
            vector_boost=vector_boost,
            filter=filter,
        )

        return cls.build_search_body(
            query=query, size=size, source=source, min_score=min_score
        )
