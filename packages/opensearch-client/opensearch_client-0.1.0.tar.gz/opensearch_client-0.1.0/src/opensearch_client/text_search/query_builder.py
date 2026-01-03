"""
텍스트 검색 쿼리 빌더

멀티매치, 퍼지 매칭, 구문 매칭 등 OpenSearch DSL 쿼리 생성
"""

from typing import Any


class TextQueryBuilder:
    """
    텍스트 검색 쿼리 빌더

    OpenSearch DSL 형식의 검색 쿼리를 생성합니다.
    """

    @staticmethod
    def multi_match(
        query: str,
        fields: list[str],
        boost_map: dict[str, float] | None = None,
        fuzziness: str = "AUTO",
        operator: str = "or",
        minimum_should_match: str | None = None,
    ) -> dict[str, Any]:
        """
        멀티 매치 쿼리 생성

        여러 필드에서 동시에 검색하며, 필드별 가중치 설정 가능

        Args:
            query: 검색어
            fields: 검색할 필드 목록
            boost_map: 필드별 가중치 (예: {"question": 2.0, "answer": 1.0})
            fuzziness: 오타 허용 수준 ("AUTO", "0", "1", "2")
            operator: 단어 간 연산자 ("or", "and")
            minimum_should_match: 최소 일치 비율 (예: "75%")

        Returns:
            멀티 매치 쿼리 DSL
        """
        # 필드에 boost 적용
        if boost_map:
            boosted_fields = []
            for field in fields:
                if field in boost_map:
                    boosted_fields.append(f"{field}^{boost_map[field]}")
                else:
                    boosted_fields.append(field)
            fields = boosted_fields

        query_body = {
            "multi_match": {
                "query": query,
                "fields": fields,
                "fuzziness": fuzziness,
                "operator": operator,
            }
        }

        if minimum_should_match:
            query_body["multi_match"]["minimum_should_match"] = minimum_should_match

        return query_body

    @staticmethod
    def match_phrase(
        field: str, query: str, boost: float = 1.0, slop: int = 0
    ) -> dict[str, Any]:
        """
        구문 일치 쿼리 생성

        정확한 구문이 포함된 문서 검색

        Args:
            field: 검색할 필드
            query: 검색 구문
            boost: 가중치
            slop: 허용되는 단어 간 거리

        Returns:
            구문 일치 쿼리 DSL
        """
        return {"match_phrase": {field: {"query": query, "boost": boost, "slop": slop}}}

    @staticmethod
    def match(
        field: str,
        query: str,
        boost: float = 1.0,
        fuzziness: str | None = None,
        operator: str = "or",
    ) -> dict[str, Any]:
        """
        단일 필드 매치 쿼리 생성

        Args:
            field: 검색할 필드
            query: 검색어
            boost: 가중치
            fuzziness: 오타 허용 수준
            operator: 단어 간 연산자

        Returns:
            매치 쿼리 DSL
        """
        query_body = {
            "match": {field: {"query": query, "boost": boost, "operator": operator}}
        }

        if fuzziness:
            query_body["match"][field]["fuzziness"] = fuzziness

        return query_body

    @staticmethod
    def bool_query(
        must: list[dict[str, Any]] | None = None,
        should: list[dict[str, Any]] | None = None,
        must_not: list[dict[str, Any]] | None = None,
        filter: list[dict[str, Any]] | None = None,
        minimum_should_match: int = 1,
    ) -> dict[str, Any]:
        """
        Bool 쿼리 생성

        여러 쿼리를 조합하여 복합 쿼리 생성

        Args:
            must: AND 조건 (점수에 영향)
            should: OR 조건 (점수에 영향)
            must_not: NOT 조건
            filter: 필터 조건 (점수에 영향 없음)
            minimum_should_match: should 절 최소 일치 개수

        Returns:
            Bool 쿼리 DSL
        """
        bool_query: dict[str, Any] = {"bool": {}}

        if must:
            bool_query["bool"]["must"] = must
        if should:
            bool_query["bool"]["should"] = should
            bool_query["bool"]["minimum_should_match"] = minimum_should_match
        if must_not:
            bool_query["bool"]["must_not"] = must_not
        if filter:
            bool_query["bool"]["filter"] = filter

        return bool_query

    @classmethod
    def korean_search_query(
        cls,
        query: str,
        primary_field: str = "question",
        secondary_field: str = "answer",
        required_text: str | None = None,
        boost_primary: float = 2.0,
        boost_secondary: float = 1.0,
        keyword_match: bool = True,
        min_should_match: str = "50%",
        required_text_boost: float = 1.5,
    ) -> dict[str, Any]:
        """
        한국어 텍스트 검색 쿼리 생성

        BREAD 프로젝트의 SearchService.search() 로직을 기반으로 함

        Args:
            query: 검색 질의
            primary_field: 주 검색 필드 (기본: "question")
            secondary_field: 보조 검색 필드 (기본: "answer")
            required_text: 결과에 반드시 포함되어야 할 텍스트
            boost_primary: 주 필드 가중치
            boost_secondary: 보조 필드 가중치
            keyword_match: 키워드 매치 모드 (True: OR, False: AND)
            min_should_match: 최소 일치 비율
            required_text_boost: 필수 텍스트 가중치

        Returns:
            검색 쿼리 DSL
        """
        # should 절: 기본 검색 쿼리
        should_clauses = [
            # 멀티 매치 (primary 가중치 높음)
            cls.multi_match(
                query=query,
                fields=[primary_field, secondary_field],
                boost_map={
                    primary_field: boost_primary,
                    secondary_field: boost_secondary,
                },
                fuzziness="AUTO",
            ),
            # secondary 구문 일치 (가장 높은 가중치)
            cls.match_phrase(secondary_field, query, boost=2.5),
            # primary 구문 일치
            cls.match_phrase(primary_field, query, boost=2.0),
        ]

        # must 절: 필수 조건
        must_clauses = []

        # 필수 텍스트가 있는 경우
        if required_text:
            operator = "or" if keyword_match else "and"

            must_clauses.append(
                {
                    "multi_match": {
                        "query": required_text,
                        "fields": [f"{secondary_field}^2.0", primary_field],
                        "operator": operator,
                        "minimum_should_match": min_should_match,
                        "fuzziness": "AUTO",
                        "boost": required_text_boost,
                    }
                }
            )

            # 필수 텍스트 구문 일치도 should에 추가
            should_clauses.append(
                cls.match_phrase(
                    secondary_field, required_text, boost=required_text_boost * 2
                )
            )

        return cls.bool_query(
            must=must_clauses if must_clauses else None,
            should=should_clauses,
            minimum_should_match=1,
        )

    @staticmethod
    def build_search_body(
        query: dict[str, Any],
        size: int = 10,
        from_: int = 0,
        sort: list[dict[str, Any]] | None = None,
        source: list[str] | None = None,
        highlight: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        완전한 검색 요청 본문 생성

        Args:
            query: 쿼리 DSL
            size: 반환할 결과 수
            from_: 시작 오프셋
            sort: 정렬 조건
            source: 반환할 필드 목록
            highlight: 하이라이팅 설정

        Returns:
            검색 요청 본문
        """
        body: dict[str, Any] = {"query": query, "size": size, "from": from_}

        if sort:
            body["sort"] = sort
        if source:
            body["_source"] = source
        if highlight:
            body["highlight"] = highlight

        return body
