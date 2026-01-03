"""
KNNSearch 단위 테스트
"""

from opensearch_client.semantic_search.knn_search import KNNSearch


class TestKNNSearch:
    """KNNSearch 테스트"""

    def test_knn_query_basic(self, sample_vector):
        """기본 k-NN 쿼리 생성"""
        query = KNNSearch.knn_query(field="vector", vector=sample_vector, k=10)

        assert "knn" in query
        assert "vector" in query["knn"]
        assert query["knn"]["vector"]["vector"] == sample_vector
        assert query["knn"]["vector"]["k"] == 10

    def test_knn_query_with_filter(self, sample_vector):
        """필터 적용 k-NN 쿼리"""
        filter_query = {"term": {"category": "tech"}}
        query = KNNSearch.knn_query(
            field="vector", vector=sample_vector, k=5, filter=filter_query
        )

        assert query["knn"]["vector"]["filter"] == filter_query

    def test_script_score_query_cosine(self, sample_vector):
        """코사인 유사도 Script Score 쿼리"""
        query = KNNSearch.script_score_query(
            field="vector", vector=sample_vector, space_type="cosinesimil"
        )

        assert "script_score" in query
        assert "cosineSimilarity" in query["script_score"]["script"]["source"]
        assert (
            query["script_score"]["script"]["params"]["query_vector"] == sample_vector
        )

    def test_script_score_query_l2(self, sample_vector):
        """L2 거리 Script Score 쿼리"""
        query = KNNSearch.script_score_query(
            field="vector", vector=sample_vector, space_type="l2"
        )

        assert "l2norm" in query["script_score"]["script"]["source"]

    def test_script_score_query_innerproduct(self, sample_vector):
        """내적 Script Score 쿼리"""
        query = KNNSearch.script_score_query(
            field="vector", vector=sample_vector, space_type="innerproduct"
        )

        assert "dotProduct" in query["script_score"]["script"]["source"]

    def test_script_score_query_with_filter(self, sample_vector):
        """필터 적용 Script Score 쿼리"""
        filter_query = {"term": {"category": "tech"}}
        query = KNNSearch.script_score_query(
            field="vector", vector=sample_vector, filter=filter_query
        )

        assert query["script_score"]["query"] == filter_query

    def test_script_score_query_default_filter(self, sample_vector):
        """기본 필터 (match_all) Script Score 쿼리"""
        query = KNNSearch.script_score_query(field="vector", vector=sample_vector)

        assert query["script_score"]["query"] == {"match_all": {}}

    def test_neural_query(self):
        """Neural 쿼리 생성"""
        query = KNNSearch.neural_query(
            field="vector", query_text="검색 텍스트", model_id="test-model-id", k=10
        )

        assert "neural" in query
        assert query["neural"]["vector"]["query_text"] == "검색 텍스트"
        assert query["neural"]["vector"]["model_id"] == "test-model-id"
        assert query["neural"]["vector"]["k"] == 10

    def test_build_search_body(self, sample_vector):
        """검색 본문 생성"""
        query = KNNSearch.knn_query("vector", sample_vector, k=10)
        body = KNNSearch.build_search_body(
            query=query, size=20, source=["title", "content"]
        )

        assert body["query"] == query
        assert body["size"] == 20
        assert body["_source"] == ["title", "content"]

    def test_build_search_body_with_min_score(self, sample_vector):
        """min_score 적용 검색 본문"""
        query = KNNSearch.knn_query("vector", sample_vector, k=10)
        body = KNNSearch.build_search_body(query=query, min_score=0.5)

        assert body["min_score"] == 0.5
