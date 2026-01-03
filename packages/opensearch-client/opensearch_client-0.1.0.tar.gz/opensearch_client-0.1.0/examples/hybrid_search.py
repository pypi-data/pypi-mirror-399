"""
하이브리드 검색 예제

텍스트 검색과 벡터 검색을 결합한 하이브리드 검색 방법을 보여줍니다.
OpenSearch 2.10+ 필요 (Search Pipeline 지원)
"""

import contextlib

from opensearch_client import (
    HybridQueryBuilder,
    IndexManager,
    OpenSearchClient,
)


def create_sample_embeddings(
    texts: list[str], dimension: int = 384
) -> list[list[float]]:
    """
    샘플 임베딩 생성 (데모용)

    실제 사용 시에는 OpenAIEmbedding 또는 FastEmbedEmbedding 사용
    """
    import hashlib

    embeddings = []
    for text in texts:
        # 텍스트 해시를 기반으로 결정적 벡터 생성
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        vector = [(hash_val >> (i % 32) & 0xFFFF) / 65535.0 for i in range(dimension)]
        embeddings.append(vector)

    return embeddings


def main():
    # 1. 클라이언트 초기화
    client = OpenSearchClient(host="localhost", port=9200, use_ssl=False)

    if not client.ping():
        print("OpenSearch에 연결할 수 없습니다.")
        return

    print("OpenSearch 연결 성공!")

    # 2. 하이브리드 인덱스 생성
    index_name = "example-hybrid-search"
    pipeline_id = "example-hybrid-pipeline"

    if client.index_exists(index_name):
        client.delete_index(index_name)

    # 텍스트 + 벡터 필드가 있는 하이브리드 인덱스
    body = IndexManager.create_hybrid_index_body(
        text_fields={"content": "text"},
        vector_field="embedding",
        vector_dimension=384,
        use_korean_analyzer=True,
    )
    client.create_index(index_name, body)
    print(f"하이브리드 인덱스 '{index_name}' 생성 완료")

    # 3. Search Pipeline 설정
    with contextlib.suppress(Exception):
        client.delete_search_pipeline(pipeline_id)

    client.setup_hybrid_pipeline(
        pipeline_id=pipeline_id,
        text_weight=0.3,  # 텍스트 점수 30%
        vector_weight=0.7,  # 벡터 점수 70%
    )
    print(f"Search Pipeline '{pipeline_id}' 생성 완료")

    # 4. 문서 준비 및 임베딩 생성
    documents = [
        {
            "title": "빵 만들기",
            "content": "빵은 밀가루와 물, 이스트를 넣어 반죽하여 만듭니다.",
        },
        {
            "title": "케이크 레시피",
            "content": "케이크는 밀가루, 달걀, 설탕, 버터로 만드는 디저트입니다.",
        },
        {
            "title": "파이썬 기초",
            "content": "파이썬은 배우기 쉬운 프로그래밍 언어입니다.",
        },
        {
            "title": "OpenSearch 검색",
            "content": "OpenSearch는 텍스트와 벡터 검색을 지원합니다.",
        },
        {
            "title": "기계학습 입문",
            "content": "기계학습은 데이터에서 패턴을 학습하는 기술입니다.",
        },
    ]

    # 임베딩 생성
    contents = [doc["content"] for doc in documents]
    embeddings = create_sample_embeddings(contents)

    # 임베딩 추가
    for doc, emb in zip(documents, embeddings, strict=True):
        doc["embedding"] = emb

    # 5. 문서 인덱싱
    client.bulk_index(index_name, documents)
    client.refresh(index_name)
    print(f"{len(documents)}개 문서 인덱싱 완료")

    # 6. 하이브리드 검색
    search_query = "밀가루로 만드는 음식"
    query_embedding = create_sample_embeddings([search_query])[0]

    print(f"\n=== 하이브리드 검색: '{search_query}' ===")

    # 하이브리드 쿼리 생성
    hybrid_query = HybridQueryBuilder.build_hybrid_query(
        text_query=search_query,
        query_vector=query_embedding,
        text_fields=["content"],
        vector_field="embedding",
        k=5,
    )

    body = HybridQueryBuilder.build_search_body(
        query=hybrid_query, size=5, source=["title", "content"]
    )

    # Search Pipeline과 함께 검색
    result = client.search(index_name, body, params={"search_pipeline": pipeline_id})

    print("\n검색 결과:")
    for i, hit in enumerate(result["hits"]["hits"], 1):
        print(f"  {i}. {hit['_source']['title']}")
        print(f"     내용: {hit['_source']['content'][:50]}...")
        print(f"     점수: {hit['_score']:.4f}")
        print()

    # 7. RRF (Reciprocal Rank Fusion) 파이프라인 예제
    rrf_pipeline_id = "example-rrf-pipeline"

    with contextlib.suppress(Exception):
        client.delete_search_pipeline(rrf_pipeline_id)

    # RRF는 OpenSearch 2.19+ 에서 지원
    # client.setup_hybrid_pipeline(
    #     pipeline_id=rrf_pipeline_id,
    #     use_rrf=True
    # )
    # print(f"\nRRF Pipeline '{rrf_pipeline_id}' 생성 완료")

    # 8. 정리
    client.delete_search_pipeline(pipeline_id)
    client.delete_index(index_name)
    print("\n리소스 정리 완료")


if __name__ == "__main__":
    main()
