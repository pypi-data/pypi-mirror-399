"""IndexManager 유닛 테스트"""

from opensearch_client.index import IndexManager


class TestGetKoreanAnalyzerSettings:
    """get_korean_analyzer_settings() 테스트"""

    def test_returns_analysis_key(self):
        """analysis 키를 포함해야 함"""
        result = IndexManager.get_korean_analyzer_settings()
        assert "analysis" in result

    def test_contains_korean_analyzer(self):
        """korean 분석기를 포함해야 함"""
        result = IndexManager.get_korean_analyzer_settings()
        assert "korean" in result["analysis"]["analyzer"]

    def test_contains_korean_search_analyzer(self):
        """korean_search 분석기를 포함해야 함"""
        result = IndexManager.get_korean_analyzer_settings()
        assert "korean_search" in result["analysis"]["analyzer"]

    def test_korean_analyzer_uses_nori_tokenizer(self):
        """korean 분석기는 nori_tokenizer를 사용해야 함"""
        result = IndexManager.get_korean_analyzer_settings()
        analyzer = result["analysis"]["analyzer"]["korean"]
        assert analyzer["tokenizer"] == "nori_tokenizer"

    def test_nori_tokenizer_decompound_mode(self):
        """nori_tokenizer는 mixed 모드를 사용해야 함"""
        result = IndexManager.get_korean_analyzer_settings()
        tokenizer = result["analysis"]["tokenizer"]["nori_tokenizer"]
        assert tokenizer["decompound_mode"] == "mixed"


class TestGetTextIndexMapping:
    """get_text_index_mapping() 테스트"""

    def test_default_fields(self):
        """기본 필드(title, question, answer)가 포함되어야 함"""
        result = IndexManager.get_text_index_mapping()
        props = result["properties"]
        assert "title" in props
        assert "question" in props
        assert "answer" in props

    def test_custom_fields(self):
        """커스텀 필드가 적용되어야 함"""
        custom_fields = {"content": "text", "summary": "text"}
        result = IndexManager.get_text_index_mapping(text_fields=custom_fields)
        props = result["properties"]
        assert "content" in props
        assert "summary" in props
        assert "title" not in props

    def test_text_field_uses_analyzer(self):
        """text 타입 필드는 분석기를 사용해야 함"""
        result = IndexManager.get_text_index_mapping()
        assert result["properties"]["title"]["analyzer"] == "korean"

    def test_custom_analyzer(self):
        """커스텀 분석기가 적용되어야 함"""
        result = IndexManager.get_text_index_mapping(analyzer="standard")
        assert result["properties"]["title"]["analyzer"] == "standard"

    def test_non_text_field_type(self):
        """text가 아닌 타입은 그대로 사용되어야 함"""
        custom_fields = {"count": "integer", "price": "float"}
        result = IndexManager.get_text_index_mapping(text_fields=custom_fields)
        assert result["properties"]["count"]["type"] == "integer"
        assert result["properties"]["price"]["type"] == "float"

    def test_includes_metadata_fields(self):
        """메타데이터 필드가 포함되어야 함"""
        result = IndexManager.get_text_index_mapping()
        props = result["properties"]
        assert props["source_id"]["type"] == "keyword"
        assert props["source_path"]["type"] == "keyword"
        assert props["file_type"]["type"] == "keyword"
        assert props["created_at"]["type"] == "date"


class TestGetKnnIndexSettings:
    """get_knn_index_settings() 테스트"""

    def test_knn_enabled(self):
        """knn이 활성화되어야 함"""
        result = IndexManager.get_knn_index_settings()
        assert result["index"]["knn"] is True

    def test_default_ef_search(self):
        """기본 ef_search 값은 100"""
        result = IndexManager.get_knn_index_settings()
        assert result["index"]["knn.algo_param.ef_search"] == 100

    def test_custom_ef_search(self):
        """커스텀 ef_search 값이 적용되어야 함"""
        result = IndexManager.get_knn_index_settings(ef_search=200)
        assert result["index"]["knn.algo_param.ef_search"] == 200


class TestGetKnnFieldMapping:
    """get_knn_field_mapping() 테스트"""

    def test_default_field_name(self):
        """기본 필드명은 'vector'"""
        result = IndexManager.get_knn_field_mapping()
        assert "vector" in result

    def test_custom_field_name(self):
        """커스텀 필드명이 적용되어야 함"""
        result = IndexManager.get_knn_field_mapping(field_name="embedding")
        assert "embedding" in result
        assert "vector" not in result

    def test_default_dimension(self):
        """기본 차원은 1536"""
        result = IndexManager.get_knn_field_mapping()
        assert result["vector"]["dimension"] == 1536

    def test_custom_dimension(self):
        """커스텀 차원이 적용되어야 함"""
        result = IndexManager.get_knn_field_mapping(dimension=384)
        assert result["vector"]["dimension"] == 384

    def test_knn_vector_type(self):
        """타입은 knn_vector"""
        result = IndexManager.get_knn_field_mapping()
        assert result["vector"]["type"] == "knn_vector"

    def test_default_space_type(self):
        """기본 space_type은 cosinesimil"""
        result = IndexManager.get_knn_field_mapping()
        assert result["vector"]["method"]["space_type"] == "cosinesimil"

    def test_custom_space_type(self):
        """커스텀 space_type이 적용되어야 함"""
        result = IndexManager.get_knn_field_mapping(space_type="l2")
        assert result["vector"]["method"]["space_type"] == "l2"

    def test_default_engine(self):
        """기본 엔진은 lucene"""
        result = IndexManager.get_knn_field_mapping()
        assert result["vector"]["method"]["engine"] == "lucene"

    def test_hnsw_parameters(self):
        """HNSW 파라미터가 포함되어야 함"""
        result = IndexManager.get_knn_field_mapping()
        params = result["vector"]["method"]["parameters"]
        assert params["ef_construction"] == 128
        assert params["m"] == 16

    def test_custom_hnsw_parameters(self):
        """커스텀 HNSW 파라미터가 적용되어야 함"""
        result = IndexManager.get_knn_field_mapping(ef_construction=256, m=32)
        params = result["vector"]["method"]["parameters"]
        assert params["ef_construction"] == 256
        assert params["m"] == 32


class TestCreateHybridIndexBody:
    """create_hybrid_index_body() 테스트"""

    def test_returns_settings_and_mappings(self):
        """settings와 mappings를 포함해야 함"""
        result = IndexManager.create_hybrid_index_body()
        assert "settings" in result
        assert "mappings" in result

    def test_includes_korean_analyzer_by_default(self):
        """기본적으로 한국어 분석기가 포함되어야 함"""
        result = IndexManager.create_hybrid_index_body()
        assert "analysis" in result["settings"]

    def test_without_korean_analyzer(self):
        """use_korean_analyzer=False 시 분석기 미포함"""
        result = IndexManager.create_hybrid_index_body(use_korean_analyzer=False)
        assert "analysis" not in result["settings"]

    def test_includes_knn_settings(self):
        """k-NN 설정이 포함되어야 함"""
        result = IndexManager.create_hybrid_index_body()
        assert result["settings"]["index"]["knn"] is True

    def test_includes_vector_field(self):
        """벡터 필드가 포함되어야 함"""
        result = IndexManager.create_hybrid_index_body()
        props = result["mappings"]["properties"]
        assert "vector" in props
        assert props["vector"]["type"] == "knn_vector"

    def test_custom_vector_field(self):
        """커스텀 벡터 필드명이 적용되어야 함"""
        result = IndexManager.create_hybrid_index_body(vector_field="embedding")
        props = result["mappings"]["properties"]
        assert "embedding" in props
        assert "vector" not in props

    def test_custom_vector_dimension(self):
        """커스텀 벡터 차원이 적용되어야 함"""
        result = IndexManager.create_hybrid_index_body(vector_dimension=384)
        props = result["mappings"]["properties"]
        assert props["vector"]["dimension"] == 384

    def test_custom_text_fields(self):
        """커스텀 텍스트 필드가 적용되어야 함"""
        text_fields = {"content": "text", "description": "text"}
        result = IndexManager.create_hybrid_index_body(text_fields=text_fields)
        props = result["mappings"]["properties"]
        assert "content" in props
        assert "description" in props


class TestCreateTextIndexBody:
    """create_text_index_body() 테스트"""

    def test_returns_settings_and_mappings(self):
        """settings와 mappings를 포함해야 함"""
        result = IndexManager.create_text_index_body()
        assert "settings" in result
        assert "mappings" in result

    def test_default_text_field(self):
        """기본 텍스트 필드는 'content'"""
        result = IndexManager.create_text_index_body()
        props = result["mappings"]["properties"]
        assert "content" in props

    def test_custom_text_field(self):
        """커스텀 텍스트 필드가 적용되어야 함"""
        result = IndexManager.create_text_index_body(text_field="body")
        props = result["mappings"]["properties"]
        assert "body" in props
        assert "content" not in props

    def test_with_korean_analyzer(self):
        """use_korean_analyzer=True 시 분석기 포함"""
        result = IndexManager.create_text_index_body(use_korean_analyzer=True)
        assert "analysis" in result["settings"]

    def test_without_korean_analyzer(self):
        """use_korean_analyzer=False 시 분석기 미포함"""
        result = IndexManager.create_text_index_body(use_korean_analyzer=False)
        assert result["settings"] == {}

    def test_uses_korean_analyzer_for_field(self):
        """use_korean_analyzer=True 시 korean 분석기 사용"""
        result = IndexManager.create_text_index_body(use_korean_analyzer=True)
        props = result["mappings"]["properties"]
        assert props["content"]["analyzer"] == "korean"

    def test_uses_standard_analyzer_for_field(self):
        """use_korean_analyzer=False 시 standard 분석기 사용"""
        result = IndexManager.create_text_index_body(use_korean_analyzer=False)
        props = result["mappings"]["properties"]
        assert props["content"]["analyzer"] == "standard"

    def test_additional_fields(self):
        """추가 필드가 적용되어야 함"""
        additional = {"title": "text", "tags": "keyword"}
        result = IndexManager.create_text_index_body(additional_fields=additional)
        props = result["mappings"]["properties"]
        assert "content" in props
        assert "title" in props
        assert props["tags"]["type"] == "keyword"


class TestCreateVectorIndexBody:
    """create_vector_index_body() 테스트"""

    def test_returns_settings_and_mappings(self):
        """settings와 mappings를 포함해야 함"""
        result = IndexManager.create_vector_index_body()
        assert "settings" in result
        assert "mappings" in result

    def test_includes_knn_settings(self):
        """k-NN 설정이 포함되어야 함"""
        result = IndexManager.create_vector_index_body()
        assert result["settings"]["index"]["knn"] is True

    def test_default_vector_field(self):
        """기본 벡터 필드는 'vector'"""
        result = IndexManager.create_vector_index_body()
        props = result["mappings"]["properties"]
        assert "vector" in props

    def test_custom_vector_field(self):
        """커스텀 벡터 필드가 적용되어야 함"""
        result = IndexManager.create_vector_index_body(vector_field="embedding")
        props = result["mappings"]["properties"]
        assert "embedding" in props
        assert "vector" not in props

    def test_default_dimension(self):
        """기본 차원은 1536"""
        result = IndexManager.create_vector_index_body()
        props = result["mappings"]["properties"]
        assert props["vector"]["dimension"] == 1536

    def test_custom_dimension(self):
        """커스텀 차원이 적용되어야 함"""
        result = IndexManager.create_vector_index_body(vector_dimension=768)
        props = result["mappings"]["properties"]
        assert props["vector"]["dimension"] == 768

    def test_includes_text_field(self):
        """기본 text 필드가 포함되어야 함"""
        result = IndexManager.create_vector_index_body()
        props = result["mappings"]["properties"]
        assert "text" in props
        assert props["text"]["type"] == "text"

    def test_custom_space_type(self):
        """커스텀 space_type이 적용되어야 함"""
        result = IndexManager.create_vector_index_body(space_type="innerproduct")
        props = result["mappings"]["properties"]
        assert props["vector"]["method"]["space_type"] == "innerproduct"
