"""
SearchPipelineManager 단위 테스트
"""

from opensearch_client.hybrid_search.pipeline import (
    CombinationType,
    NormalizationType,
    SearchPipelineManager,
)


class TestSearchPipelineManager:
    """SearchPipelineManager 테스트"""

    def test_create_normalization_processor_default(self):
        """기본 정규화 프로세서 생성"""
        processor = SearchPipelineManager.create_normalization_processor()

        assert "normalization-processor" in processor
        np = processor["normalization-processor"]
        assert np["normalization"]["technique"] == "min_max"
        assert np["combination"]["technique"] == "arithmetic_mean"

    def test_create_normalization_processor_l2(self):
        """L2 정규화 프로세서"""
        processor = SearchPipelineManager.create_normalization_processor(
            normalization_technique=NormalizationType.L2
        )

        np = processor["normalization-processor"]
        assert np["normalization"]["technique"] == "l2"

    def test_create_normalization_processor_with_weights(self):
        """가중치 적용 정규화 프로세서"""
        processor = SearchPipelineManager.create_normalization_processor(
            weights=[0.3, 0.7]
        )

        np = processor["normalization-processor"]
        assert np["combination"]["parameters"]["weights"] == [0.3, 0.7]

    def test_create_normalization_processor_geometric_mean(self):
        """기하 평균 결합 프로세서"""
        processor = SearchPipelineManager.create_normalization_processor(
            combination_technique=CombinationType.GEOMETRIC_MEAN
        )

        np = processor["normalization-processor"]
        assert np["combination"]["technique"] == "geometric_mean"

    def test_create_rrf_processor(self):
        """RRF 프로세서 생성"""
        processor = SearchPipelineManager.create_rrf_processor()

        assert "score-ranker-processor" in processor
        srp = processor["score-ranker-processor"]
        assert srp["combination"]["technique"] == "rrf"
        assert srp["combination"]["parameters"]["rank_constant"] == 60
        assert srp["combination"]["parameters"]["window_size"] == 100

    def test_create_rrf_processor_custom_params(self):
        """커스텀 파라미터 RRF 프로세서"""
        processor = SearchPipelineManager.create_rrf_processor(
            rank_constant=30, window_size=50
        )

        srp = processor["score-ranker-processor"]
        assert srp["combination"]["parameters"]["rank_constant"] == 30
        assert srp["combination"]["parameters"]["window_size"] == 50

    def test_build_pipeline_body_normalization(self):
        """정규화 파이프라인 본문 생성"""
        body = SearchPipelineManager.build_pipeline_body(
            description="Test pipeline", use_rrf=False, weights=[0.4, 0.6]
        )

        assert body["description"] == "Test pipeline"
        assert len(body["phase_results_processors"]) == 1
        assert "normalization-processor" in body["phase_results_processors"][0]

    def test_build_pipeline_body_rrf(self):
        """RRF 파이프라인 본문 생성"""
        body = SearchPipelineManager.build_pipeline_body(use_rrf=True, rank_constant=40)

        assert len(body["phase_results_processors"]) == 1
        assert "score-ranker-processor" in body["phase_results_processors"][0]

    def test_build_default_hybrid_pipeline(self):
        """기본 하이브리드 파이프라인 생성"""
        body = SearchPipelineManager.build_default_hybrid_pipeline(
            text_weight=0.3, vector_weight=0.7
        )

        assert "description" in body
        assert len(body["phase_results_processors"]) == 1

        np = body["phase_results_processors"][0]["normalization-processor"]
        assert np["combination"]["parameters"]["weights"] == [0.3, 0.7]

    def test_build_default_hybrid_pipeline_equal_weights(self):
        """동일 가중치 하이브리드 파이프라인"""
        body = SearchPipelineManager.build_default_hybrid_pipeline(
            text_weight=0.5, vector_weight=0.5
        )

        np = body["phase_results_processors"][0]["normalization-processor"]
        assert np["combination"]["parameters"]["weights"] == [0.5, 0.5]
