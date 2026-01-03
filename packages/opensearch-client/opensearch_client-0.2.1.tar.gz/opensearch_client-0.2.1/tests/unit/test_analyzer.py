"""AnalyzerConfig 유닛 테스트"""

from opensearch_client.text_search.analyzer import AnalyzerConfig, DecompoundMode


class TestDecompoundMode:
    """DecompoundMode enum 테스트"""

    def test_none_value(self):
        """NONE 값 확인"""
        assert DecompoundMode.NONE.value == "none"

    def test_discard_value(self):
        """DISCARD 값 확인"""
        assert DecompoundMode.DISCARD.value == "discard"

    def test_mixed_value(self):
        """MIXED 값 확인"""
        assert DecompoundMode.MIXED.value == "mixed"


class TestKoreanAnalyzer:
    """korean_analyzer() 테스트"""

    def test_returns_analysis_key(self):
        """analysis 키를 포함해야 함"""
        result = AnalyzerConfig.korean_analyzer()
        assert "analysis" in result

    def test_default_analyzer_name(self):
        """기본 분석기 이름은 'korean'"""
        result = AnalyzerConfig.korean_analyzer()
        assert "korean" in result["analysis"]["analyzer"]

    def test_custom_analyzer_name(self):
        """커스텀 분석기 이름이 적용되어야 함"""
        result = AnalyzerConfig.korean_analyzer(name="my_korean")
        assert "my_korean" in result["analysis"]["analyzer"]
        assert "korean" not in result["analysis"]["analyzer"]

    def test_default_decompound_mode(self):
        """기본 decompound_mode는 'mixed'"""
        result = AnalyzerConfig.korean_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert tokenizer["decompound_mode"] == "mixed"

    def test_custom_decompound_mode_none(self):
        """NONE decompound_mode 적용"""
        result = AnalyzerConfig.korean_analyzer(decompound_mode=DecompoundMode.NONE)
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert tokenizer["decompound_mode"] == "none"

    def test_custom_decompound_mode_discard(self):
        """DISCARD decompound_mode 적용"""
        result = AnalyzerConfig.korean_analyzer(decompound_mode=DecompoundMode.DISCARD)
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert tokenizer["decompound_mode"] == "discard"

    def test_tokenizer_type(self):
        """토크나이저 타입은 'nori_tokenizer'"""
        result = AnalyzerConfig.korean_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert tokenizer["type"] == "nori_tokenizer"

    def test_includes_lowercase_filter(self):
        """lowercase 필터가 포함되어야 함"""
        result = AnalyzerConfig.korean_analyzer()
        analyzer = result["analysis"]["analyzer"]["korean"]
        assert "lowercase" in analyzer["filter"]

    def test_includes_nori_readingform_filter(self):
        """nori_readingform 필터가 포함되어야 함"""
        result = AnalyzerConfig.korean_analyzer()
        analyzer = result["analysis"]["analyzer"]["korean"]
        assert "nori_readingform" in analyzer["filter"]

    def test_user_dictionary(self):
        """user_dictionary가 적용되어야 함"""
        result = AnalyzerConfig.korean_analyzer(user_dictionary="/path/to/dict.txt")
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert tokenizer["user_dictionary"] == "/path/to/dict.txt"

    def test_without_user_dictionary(self):
        """user_dictionary 미지정 시 키가 없어야 함"""
        result = AnalyzerConfig.korean_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["korean_tokenizer"]
        assert "user_dictionary" not in tokenizer

    def test_custom_stoptags(self):
        """커스텀 stoptags가 적용되어야 함"""
        custom_stoptags = ["E", "J", "SP"]
        result = AnalyzerConfig.korean_analyzer(stoptags=custom_stoptags)
        filter_config = result["analysis"]["filter"]["nori_stoptags"]
        assert filter_config["stoptags"] == custom_stoptags

    def test_stoptags_adds_filter(self):
        """stoptags 지정 시 nori_stoptags 필터가 추가되어야 함"""
        result = AnalyzerConfig.korean_analyzer(stoptags=["E", "J"])
        analyzer = result["analysis"]["analyzer"]["korean"]
        assert "nori_stoptags" in analyzer["filter"]

    def test_default_stoptags_values(self):
        """기본 stoptags 값이 설정되어야 함"""
        result = AnalyzerConfig.korean_analyzer(stoptags=None)
        filter_config = result["analysis"]["filter"]["nori_stoptags"]
        # 기본 stoptags에 포함되어야 하는 값들 확인
        assert "E" in filter_config["stoptags"]  # 어미
        assert "J" in filter_config["stoptags"]  # 조사
        assert "SP" in filter_config["stoptags"]  # 공백


class TestStandardAnalyzer:
    """standard_analyzer() 테스트"""

    def test_returns_analysis_key(self):
        """analysis 키를 포함해야 함"""
        result = AnalyzerConfig.standard_analyzer()
        assert "analysis" in result

    def test_default_analyzer_name(self):
        """기본 분석기 이름은 'standard_custom'"""
        result = AnalyzerConfig.standard_analyzer()
        assert "standard_custom" in result["analysis"]["analyzer"]

    def test_custom_analyzer_name(self):
        """커스텀 분석기 이름이 적용되어야 함"""
        result = AnalyzerConfig.standard_analyzer(name="my_standard")
        assert "my_standard" in result["analysis"]["analyzer"]

    def test_tokenizer_type(self):
        """토크나이저 타입은 'standard'"""
        result = AnalyzerConfig.standard_analyzer()
        analyzer = result["analysis"]["analyzer"]["standard_custom"]
        assert analyzer["tokenizer"] == "standard"

    def test_includes_lowercase_filter(self):
        """lowercase 필터가 포함되어야 함"""
        result = AnalyzerConfig.standard_analyzer()
        analyzer = result["analysis"]["analyzer"]["standard_custom"]
        assert "lowercase" in analyzer["filter"]

    def test_includes_asciifolding_filter(self):
        """asciifolding 필터가 포함되어야 함"""
        result = AnalyzerConfig.standard_analyzer()
        analyzer = result["analysis"]["analyzer"]["standard_custom"]
        assert "asciifolding" in analyzer["filter"]


class TestWhitespaceAnalyzer:
    """whitespace_analyzer() 테스트"""

    def test_returns_analysis_key(self):
        """analysis 키를 포함해야 함"""
        result = AnalyzerConfig.whitespace_analyzer()
        assert "analysis" in result

    def test_default_analyzer_name(self):
        """기본 분석기 이름은 'whitespace_custom'"""
        result = AnalyzerConfig.whitespace_analyzer()
        assert "whitespace_custom" in result["analysis"]["analyzer"]

    def test_custom_analyzer_name(self):
        """커스텀 분석기 이름이 적용되어야 함"""
        result = AnalyzerConfig.whitespace_analyzer(name="my_whitespace")
        assert "my_whitespace" in result["analysis"]["analyzer"]

    def test_tokenizer_type(self):
        """토크나이저 타입은 'whitespace'"""
        result = AnalyzerConfig.whitespace_analyzer()
        analyzer = result["analysis"]["analyzer"]["whitespace_custom"]
        assert analyzer["tokenizer"] == "whitespace"

    def test_includes_lowercase_filter(self):
        """lowercase 필터가 포함되어야 함"""
        result = AnalyzerConfig.whitespace_analyzer()
        analyzer = result["analysis"]["analyzer"]["whitespace_custom"]
        assert "lowercase" in analyzer["filter"]


class TestNgramAnalyzer:
    """ngram_analyzer() 테스트"""

    def test_returns_analysis_key(self):
        """analysis 키를 포함해야 함"""
        result = AnalyzerConfig.ngram_analyzer()
        assert "analysis" in result

    def test_default_analyzer_name(self):
        """기본 분석기 이름은 'ngram_analyzer'"""
        result = AnalyzerConfig.ngram_analyzer()
        assert "ngram_analyzer" in result["analysis"]["analyzer"]

    def test_custom_analyzer_name(self):
        """커스텀 분석기 이름이 적용되어야 함"""
        result = AnalyzerConfig.ngram_analyzer(name="my_ngram")
        assert "my_ngram" in result["analysis"]["analyzer"]

    def test_default_min_gram(self):
        """기본 min_gram은 2"""
        result = AnalyzerConfig.ngram_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert tokenizer["min_gram"] == 2

    def test_default_max_gram(self):
        """기본 max_gram은 3"""
        result = AnalyzerConfig.ngram_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert tokenizer["max_gram"] == 3

    def test_custom_min_gram(self):
        """커스텀 min_gram이 적용되어야 함"""
        result = AnalyzerConfig.ngram_analyzer(min_gram=1)
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert tokenizer["min_gram"] == 1

    def test_custom_max_gram(self):
        """커스텀 max_gram이 적용되어야 함"""
        result = AnalyzerConfig.ngram_analyzer(max_gram=5)
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert tokenizer["max_gram"] == 5

    def test_tokenizer_type(self):
        """토크나이저 타입은 'ngram'"""
        result = AnalyzerConfig.ngram_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert tokenizer["type"] == "ngram"

    def test_token_chars(self):
        """token_chars가 설정되어야 함"""
        result = AnalyzerConfig.ngram_analyzer()
        tokenizer = result["analysis"]["tokenizer"]["ngram_analyzer_tokenizer"]
        assert "letter" in tokenizer["token_chars"]
        assert "digit" in tokenizer["token_chars"]


class TestMergeSettings:
    """merge_settings() 테스트"""

    def test_merge_two_analyzers(self):
        """두 분석기 설정을 병합해야 함"""
        korean = AnalyzerConfig.korean_analyzer(name="korean")
        standard = AnalyzerConfig.standard_analyzer(name="standard")
        result = AnalyzerConfig.merge_settings(korean, standard)

        assert "korean" in result["analysis"]["analyzer"]
        assert "standard" in result["analysis"]["analyzer"]

    def test_merge_tokenizers(self):
        """토크나이저가 병합되어야 함"""
        korean = AnalyzerConfig.korean_analyzer(name="korean")
        ngram = AnalyzerConfig.ngram_analyzer(name="ngram")
        result = AnalyzerConfig.merge_settings(korean, ngram)

        assert "korean_tokenizer" in result["analysis"]["tokenizer"]
        assert "ngram_tokenizer" in result["analysis"]["tokenizer"]

    def test_merge_filters(self):
        """필터가 병합되어야 함"""
        korean = AnalyzerConfig.korean_analyzer(name="korean", stoptags=["E"])
        result = AnalyzerConfig.merge_settings(korean)

        assert "nori_stoptags" in result["analysis"]["filter"]

    def test_merge_empty_settings(self):
        """빈 설정 병합 시 빈 analysis 반환"""
        result = AnalyzerConfig.merge_settings({}, {})
        assert result == {"analysis": {}}

    def test_merge_without_analysis_key(self):
        """analysis 키가 없는 설정은 무시"""
        valid = AnalyzerConfig.standard_analyzer()
        invalid = {"other": "value"}
        result = AnalyzerConfig.merge_settings(valid, invalid)

        assert "standard_custom" in result["analysis"]["analyzer"]

    def test_merge_three_settings(self):
        """세 개 이상의 설정 병합"""
        korean = AnalyzerConfig.korean_analyzer(name="korean")
        standard = AnalyzerConfig.standard_analyzer(name="standard")
        whitespace = AnalyzerConfig.whitespace_analyzer(name="whitespace")
        result = AnalyzerConfig.merge_settings(korean, standard, whitespace)

        assert "korean" in result["analysis"]["analyzer"]
        assert "standard" in result["analysis"]["analyzer"]
        assert "whitespace" in result["analysis"]["analyzer"]

    def test_merge_preserves_analyzer_config(self):
        """병합 시 분석기 설정이 보존되어야 함"""
        korean = AnalyzerConfig.korean_analyzer(name="korean")
        result = AnalyzerConfig.merge_settings(korean)

        analyzer = result["analysis"]["analyzer"]["korean"]
        assert analyzer["type"] == "custom"
        assert "lowercase" in analyzer["filter"]
