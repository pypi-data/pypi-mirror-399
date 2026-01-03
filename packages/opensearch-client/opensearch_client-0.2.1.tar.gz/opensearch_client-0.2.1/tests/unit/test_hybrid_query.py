"""
HybridQueryBuilder 단위 테스트
"""

from opensearch_client.hybrid_search import HybridQueryBuilder


class TestHybridQueryBuilder:
    """HybridQueryBuilder 테스트"""

    def test_build_text_query(self):
        """텍스트 쿼리 생성"""
        query = HybridQueryBuilder.build_text_query(
            query="검색어", fields=["title", "content"]
        )

        assert "multi_match" in query
        assert query["multi_match"]["query"] == "검색어"
        assert query["multi_match"]["fields"] == ["title", "content"]

    def test_build_text_query_default_fields(self):
        """기본 필드로 텍스트 쿼리 생성"""
        query = HybridQueryBuilder.build_text_query(query="검색어")

        assert query["multi_match"]["fields"] == ["text"]

    def test_build_text_query_with_boost(self):
        """boost 적용 텍스트 쿼리"""
        query = HybridQueryBuilder.build_text_query(query="검색어", boost=2.0)

        assert query["multi_match"]["boost"] == 2.0

    def test_build_knn_query(self, sample_vector):
        """k-NN 쿼리 생성"""
        query = HybridQueryBuilder.build_knn_query(
            vector=sample_vector, field="embedding", k=5
        )

        assert "knn" in query
        assert "embedding" in query["knn"]
        assert query["knn"]["embedding"]["vector"] == sample_vector
        assert query["knn"]["embedding"]["k"] == 5

    def test_build_knn_query_with_boost(self, sample_vector):
        """boost 적용 k-NN 쿼리"""
        query = HybridQueryBuilder.build_knn_query(vector=sample_vector, boost=1.5)

        assert query["knn"]["vector"]["boost"] == 1.5

    def test_build_hybrid_query(self, sample_vector):
        """하이브리드 쿼리 생성"""
        query = HybridQueryBuilder.build_hybrid_query(
            text_query="검색어",
            query_vector=sample_vector,
            text_fields=["title"],
            vector_field="embedding",
            k=10,
        )

        assert "hybrid" in query
        assert "queries" in query["hybrid"]
        assert len(query["hybrid"]["queries"]) == 2

        # 첫 번째는 텍스트 쿼리
        assert "multi_match" in query["hybrid"]["queries"][0]
        # 두 번째는 k-NN 쿼리
        assert "knn" in query["hybrid"]["queries"][1]

    def test_build_hybrid_query_with_filter(self, sample_vector):
        """필터 적용 하이브리드 쿼리"""
        filter_query = {"term": {"category": "tech"}}
        query = HybridQueryBuilder.build_hybrid_query(
            text_query="검색어", query_vector=sample_vector, filter=filter_query
        )

        assert query["hybrid"]["filter"] == filter_query

    def test_build_hybrid_query_with_boosts(self, sample_vector):
        """boost 적용 하이브리드 쿼리"""
        query = HybridQueryBuilder.build_hybrid_query(
            text_query="검색어",
            query_vector=sample_vector,
            text_boost=0.3,
            vector_boost=0.7,
        )

        text_query = query["hybrid"]["queries"][0]
        knn_query = query["hybrid"]["queries"][1]

        assert text_query["multi_match"]["boost"] == 0.3
        assert knn_query["knn"]["vector"]["boost"] == 0.7

    def test_build_search_body(self, sample_vector):
        """검색 본문 생성"""
        query = {"match_all": {}}
        body = HybridQueryBuilder.build_search_body(
            query=query, size=20, source=["title", "content"]
        )

        assert body["query"] == query
        assert body["size"] == 20
        assert body["_source"] == ["title", "content"]

    def test_build_search_body_with_min_score(self):
        """min_score 적용 검색 본문"""
        body = HybridQueryBuilder.build_search_body(
            query={"match_all": {}}, min_score=0.5
        )

        assert body["min_score"] == 0.5

    def test_build_complete_hybrid_search(self, sample_vector):
        """완전한 하이브리드 검색 본문 생성"""
        body = HybridQueryBuilder.build_complete_hybrid_search(
            text_query="검색어",
            query_vector=sample_vector,
            text_fields=["title", "content"],
            vector_field="embedding",
            k=10,
            size=20,
            source=["title"],
        )

        assert "query" in body
        assert "hybrid" in body["query"]
        assert body["size"] == 20
        assert body["_source"] == ["title"]
