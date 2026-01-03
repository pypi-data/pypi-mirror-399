"""
TextQueryBuilder 단위 테스트
"""

from opensearch_client.text_search import TextQueryBuilder


class TestTextQueryBuilder:
    """TextQueryBuilder 테스트"""

    def test_multi_match_basic(self):
        """기본 멀티매치 쿼리 생성"""
        query = TextQueryBuilder.multi_match(
            query="검색어", fields=["title", "content"]
        )

        assert "multi_match" in query
        assert query["multi_match"]["query"] == "검색어"
        assert query["multi_match"]["fields"] == ["title", "content"]

    def test_multi_match_with_boost_map(self):
        """boost_map 적용 멀티매치 쿼리"""
        query = TextQueryBuilder.multi_match(
            query="검색어",
            fields=["title", "content"],
            boost_map={"title": 2.0, "content": 1.0},
        )

        assert "title^2.0" in query["multi_match"]["fields"]
        assert "content^1.0" in query["multi_match"]["fields"]

    def test_multi_match_with_fuzziness(self):
        """퍼지 검색 쿼리"""
        query = TextQueryBuilder.multi_match(
            query="검색어", fields=["title"], fuzziness="AUTO"
        )

        assert query["multi_match"]["fuzziness"] == "AUTO"

    def test_multi_match_with_operator(self):
        """연산자 적용 멀티매치 쿼리"""
        query = TextQueryBuilder.multi_match(
            query="검색어", fields=["title"], operator="and"
        )

        assert query["multi_match"]["operator"] == "and"

    def test_match_phrase(self):
        """구문 매칭 쿼리 생성"""
        query = TextQueryBuilder.match_phrase(field="title", query="정확한 구문")

        assert "match_phrase" in query
        assert query["match_phrase"]["title"]["query"] == "정확한 구문"

    def test_match_phrase_with_slop(self):
        """slop 적용 구문 매칭 쿼리"""
        query = TextQueryBuilder.match_phrase(
            field="title", query="정확한 구문", slop=2
        )

        assert query["match_phrase"]["title"]["slop"] == 2

    def test_match_phrase_with_boost(self):
        """boost 적용 구문 매칭 쿼리"""
        query = TextQueryBuilder.match_phrase(
            field="title", query="정확한 구문", boost=2.5
        )

        assert query["match_phrase"]["title"]["boost"] == 2.5

    def test_match_basic(self):
        """기본 매치 쿼리"""
        query = TextQueryBuilder.match(field="title", query="검색어")

        assert "match" in query
        assert query["match"]["title"]["query"] == "검색어"

    def test_match_with_fuzziness(self):
        """퍼지 적용 매치 쿼리"""
        query = TextQueryBuilder.match(field="title", query="검색어", fuzziness="AUTO")

        assert query["match"]["title"]["fuzziness"] == "AUTO"

    def test_bool_query_with_must(self):
        """must 절 bool 쿼리"""
        queries = [{"match": {"title": "검색어"}}]
        query = TextQueryBuilder.bool_query(must=queries)

        assert "bool" in query
        assert query["bool"]["must"] == queries

    def test_bool_query_with_should(self):
        """should 절 bool 쿼리"""
        queries = [{"match": {"title": "검색어1"}}, {"match": {"title": "검색어2"}}]
        query = TextQueryBuilder.bool_query(should=queries)

        assert "bool" in query
        assert query["bool"]["should"] == queries
        assert query["bool"]["minimum_should_match"] == 1

    def test_bool_query_with_filter(self):
        """filter 절 bool 쿼리"""
        filters = [{"term": {"category": "tech"}}]
        query = TextQueryBuilder.bool_query(must=[{"match_all": {}}], filter=filters)

        assert query["bool"]["filter"] == filters

    def test_korean_search_query(self):
        """한국어 검색 쿼리 생성 (BREAD 스타일)"""
        query = TextQueryBuilder.korean_search_query(query="한국어 검색")

        assert "bool" in query
        assert "should" in query["bool"]
        # multi_match, match_phrase (answer), match_phrase (question)
        assert len(query["bool"]["should"]) == 3

    def test_korean_search_query_with_required_text(self):
        """필수 텍스트 적용 한국어 검색 쿼리"""
        query = TextQueryBuilder.korean_search_query(
            query="한국어 검색", required_text="필수 단어"
        )

        assert "must" in query["bool"]
        # 필수 텍스트가 있으면 should에 추가 clause가 포함됨
        assert len(query["bool"]["should"]) == 4

    def test_korean_search_query_boost_settings(self):
        """boost 설정 한국어 검색 쿼리"""
        query = TextQueryBuilder.korean_search_query(
            query="한국어 검색", boost_primary=3.0, boost_secondary=1.5
        )

        # multi_match 쿼리의 fields에서 boost 확인
        multi_match = query["bool"]["should"][0]
        assert "question^3.0" in multi_match["multi_match"]["fields"]
        assert "answer^1.5" in multi_match["multi_match"]["fields"]

    def test_korean_search_query_custom_fields(self):
        """커스텀 필드 한국어 검색 쿼리"""
        query = TextQueryBuilder.korean_search_query(
            query="한국어 검색",
            primary_field="title",
            secondary_field="content",
        )

        # multi_match 쿼리의 fields에서 커스텀 필드 확인
        multi_match = query["bool"]["should"][0]
        assert "title" in str(multi_match["multi_match"]["fields"])
        assert "content" in str(multi_match["multi_match"]["fields"])

    def test_build_search_body(self):
        """검색 본문 생성"""
        inner_query = {"match_all": {}}
        body = TextQueryBuilder.build_search_body(query=inner_query, size=20, from_=10)

        assert body["query"] == inner_query
        assert body["size"] == 20
        assert body["from"] == 10

    def test_build_search_body_with_source(self):
        """_source 필드 지정 검색 본문"""
        body = TextQueryBuilder.build_search_body(
            query={"match_all": {}}, source=["title", "content"]
        )

        assert body["_source"] == ["title", "content"]

    def test_build_search_body_with_sort(self):
        """정렬 적용 검색 본문"""
        body = TextQueryBuilder.build_search_body(
            query={"match_all": {}}, sort=[{"created_at": {"order": "desc"}}]
        )

        assert body["sort"] == [{"created_at": {"order": "desc"}}]

    def test_build_search_body_with_highlight(self):
        """하이라이팅 적용 검색 본문"""
        highlight = {"fields": {"title": {}, "content": {}}}
        body = TextQueryBuilder.build_search_body(
            query={"match_all": {}}, highlight=highlight
        )

        assert body["highlight"] == highlight
