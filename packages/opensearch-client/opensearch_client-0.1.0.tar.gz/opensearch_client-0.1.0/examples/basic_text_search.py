"""
텍스트 검색 기본 예제

OpenSearch 텍스트 검색 기능을 사용하는 방법을 보여줍니다.
"""

from opensearch_client import IndexManager, OpenSearchClient, TextQueryBuilder


def main():
    # 1. 클라이언트 초기화
    client = OpenSearchClient(
        host="localhost",
        port=9200,
        use_ssl=False,  # 개발 환경
    )

    # 연결 확인
    if not client.ping():
        print("OpenSearch에 연결할 수 없습니다.")
        return

    print("OpenSearch 연결 성공!")

    # 2. 인덱스 생성
    index_name = "example-text-search"

    if client.index_exists(index_name):
        client.delete_index(index_name)

    # 텍스트 인덱스 생성 (한국어 분석기 사용)
    body = IndexManager.create_text_index_body(
        text_field="content", use_korean_analyzer=True
    )
    client.create_index(index_name, body)
    print(f"인덱스 '{index_name}' 생성 완료")

    # 3. 문서 인덱싱
    documents = [
        {
            "title": "빵 만들기",
            "content": "빵은 밀가루와 물, 이스트를 넣어 만듭니다.",
            "category": "요리",
        },
        {
            "title": "파이썬 프로그래밍",
            "content": "파이썬은 간결하고 읽기 쉬운 프로그래밍 언어입니다.",
            "category": "기술",
        },
        {
            "title": "OpenSearch 소개",
            "content": "OpenSearch는 오픈소스 검색 및 분석 엔진입니다.",
            "category": "기술",
        },
        {
            "title": "한국의 문화",
            "content": "한국은 다양한 전통 문화와 현대 문화가 공존합니다.",
            "category": "문화",
        },
    ]

    client.bulk_index(index_name, documents)
    client.refresh(index_name)
    print(f"{len(documents)}개 문서 인덱싱 완료")

    # 4. 검색 예제

    # 4-1. 기본 멀티매치 검색
    print("\n=== 멀티매치 검색: '프로그래밍' ===")
    query = TextQueryBuilder.multi_match(
        query="프로그래밍",
        fields=["title", "content"],
        boost_map={"title": 2.0, "content": 1.0},
    )
    body = TextQueryBuilder.build_search_body(query, size=10)
    result = client.search(index_name, body)

    for hit in result["hits"]["hits"]:
        print(f"  - {hit['_source']['title']} (score: {hit['_score']:.2f})")

    # 4-2. 구문 검색
    print("\n=== 구문 검색: '검색 엔진' ===")
    query = TextQueryBuilder.match_phrase(field="content", query="검색 엔진")
    body = TextQueryBuilder.build_search_body(query, size=10)
    result = client.search(index_name, body)

    for hit in result["hits"]["hits"]:
        print(f"  - {hit['_source']['title']} (score: {hit['_score']:.2f})")

    # 4-3. Bool 쿼리 (복합 조건)
    print("\n=== Bool 쿼리: 기술 카테고리에서 '오픈소스' 검색 ===")
    query = TextQueryBuilder.bool_query(
        must=[{"match": {"content": "오픈소스"}}],
        filter=[{"term": {"category.keyword": "기술"}}],
    )
    body = TextQueryBuilder.build_search_body(query, size=10)
    result = client.search(index_name, body)

    for hit in result["hits"]["hits"]:
        print(f"  - {hit['_source']['title']} (score: {hit['_score']:.2f})")

    # 5. 정리
    client.delete_index(index_name)
    print(f"\n인덱스 '{index_name}' 삭제 완료")


if __name__ == "__main__":
    main()
