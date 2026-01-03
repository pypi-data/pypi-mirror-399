"""
k-NN 검색 모듈

벡터 기반 근사 최근접 이웃 검색
"""

from typing import Any

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding


class KNNSearch:
    """
    k-NN (k-Nearest Neighbors) 검색 클래스

    벡터 임베딩을 사용한 시맨틱 검색 쿼리 생성
    """

    @staticmethod
    def knn_query(
        field: str,
        vector: list[float],
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        k-NN 검색 쿼리 생성

        Args:
            field: 벡터 필드명
            vector: 쿼리 벡터
            k: 반환할 최근접 이웃 수
            filter: 추가 필터 조건

        Returns:
            k-NN 쿼리 DSL
        """
        query: dict[str, Any] = {"knn": {field: {"vector": vector, "k": k}}}

        if filter:
            query["knn"][field]["filter"] = filter

        return query

    @staticmethod
    def script_score_query(
        field: str,
        vector: list[float],
        space_type: str = "cosinesimil",
        filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Script Score 기반 벡터 검색 쿼리

        정확한 k-NN 검색 (Exact k-NN)에 사용

        Args:
            field: 벡터 필드명
            vector: 쿼리 벡터
            space_type: 유사도 측정 방법 (cosinesimil, l2, innerproduct)
            filter: 필터 조건 (기본: match_all)

        Returns:
            Script Score 쿼리 DSL
        """
        # 유사도 함수 매핑
        score_functions = {
            "cosinesimil": f"cosineSimilarity(params.query_vector, '{field}') + 1.0",
            "l2": f"1 / (1 + l2norm(params.query_vector, '{field}'))",
            "innerproduct": f"(dotProduct(params.query_vector, '{field}') + 1.0) / 2.0",
        }

        script_source = score_functions.get(space_type, score_functions["cosinesimil"])

        return {
            "script_score": {
                "query": filter or {"match_all": {}},
                "script": {"source": script_source, "params": {"query_vector": vector}},
            }
        }

    @staticmethod
    def neural_query(
        field: str, query_text: str, model_id: str, k: int = 10
    ) -> dict[str, Any]:
        """
        Neural 검색 쿼리 생성

        OpenSearch ML 플러그인의 모델을 사용한 검색

        Args:
            field: 벡터 필드명
            query_text: 검색 텍스트 (모델이 임베딩으로 변환)
            model_id: OpenSearch에 등록된 모델 ID
            k: 반환할 결과 수

        Returns:
            Neural 쿼리 DSL
        """
        return {
            "neural": {field: {"query_text": query_text, "model_id": model_id, "k": k}}
        }

    @classmethod
    def build_search_body(
        cls,
        query: dict[str, Any],
        size: int = 10,
        source: list[str] | None = None,
        min_score: float | None = None,
    ) -> dict[str, Any]:
        """
        검색 요청 본문 생성

        Args:
            query: 쿼리 DSL
            size: 반환할 결과 수
            source: 반환할 필드 목록
            min_score: 최소 점수 임계값

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
    def search_with_embedding(
        cls,
        embedder: BaseEmbedding,
        query_text: str,
        field: str = "vector",
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        임베딩 모델을 사용한 검색 쿼리 생성

        Args:
            embedder: 임베딩 모델 인스턴스
            query_text: 검색 텍스트
            field: 벡터 필드명
            k: 반환할 결과 수
            filter: 추가 필터 조건

        Returns:
            k-NN 검색 쿼리 DSL
        """
        vector = embedder.embed(query_text)
        return cls.knn_query(field, vector, k, filter)
