"""
임베딩 모델 사용 예제

OpenAI 또는 FastEmbed 임베딩 모델을 사용하는 방법을 보여줍니다.
"""

from opensearch_client import IndexManager, OpenSearchClient
from opensearch_client.semantic_search.knn_search import KNNSearch


def example_with_fastembed():
    """
    FastEmbed (로컬 임베딩) 사용 예제

    설치: uv add opensearch-client[local]
    """
    try:
        from opensearch_client.semantic_search.embeddings import FastEmbedEmbedding
    except ImportError:
        print("FastEmbed가 설치되지 않았습니다.")
        print("설치: uv add opensearch-client[local]")
        return

    # FastEmbed 임베딩 모델 초기화
    embedder = FastEmbedEmbedding(
        model_name="BAAI/bge-small-en-v1.5"  # 384 차원
    )
    print(f"FastEmbed 모델: {embedder.model_name}")
    print(f"벡터 차원: {embedder.dimension}")

    # 단일 텍스트 임베딩
    text = "OpenSearch는 검색 엔진입니다."
    vector = embedder.embed(text)
    print(f"\n단일 임베딩 결과 (처음 5개): {vector[:5]}")

    # 배치 임베딩
    texts = [
        "첫 번째 문서입니다.",
        "두 번째 문서입니다.",
        "세 번째 문서입니다.",
    ]
    vectors = embedder.embed_batch(texts)
    print(f"\n배치 임베딩 결과: {len(vectors)}개 벡터 생성")

    return embedder


def example_with_openai():
    """
    OpenAI 임베딩 사용 예제

    설치: uv add opensearch-client[openai]
    환경변수: OPENAI_API_KEY 설정 필요
    """
    try:
        from opensearch_client.semantic_search.embeddings import OpenAIEmbedding
    except ImportError:
        print("OpenAI가 설치되지 않았습니다.")
        print("설치: uv add opensearch-client[openai]")
        return

    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    # OpenAI 임베딩 모델 초기화
    embedder = OpenAIEmbedding(
        model_name="text-embedding-3-small",
        dimensions=1536,  # 또는 더 작은 차원으로 축소 가능
    )
    print(f"OpenAI 모델: {embedder.model_name}")
    print(f"벡터 차원: {embedder.dimension}")

    # 단일 텍스트 임베딩
    text = "OpenSearch는 검색 엔진입니다."
    vector = embedder.embed(text)
    print(f"\n단일 임베딩 결과 (처음 5개): {vector[:5]}")

    return embedder


def semantic_search_example(embedder, client=None):
    """
    시맨틱 검색 예제
    """
    if client is None:
        client = OpenSearchClient(host="localhost", port=9200, use_ssl=False)

    if not client.ping():
        print("OpenSearch에 연결할 수 없습니다.")
        return

    index_name = "example-semantic-search"

    # 인덱스 생성
    if client.index_exists(index_name):
        client.delete_index(index_name)

    body = IndexManager.create_vector_index_body(
        vector_field="embedding", vector_dimension=embedder.dimension
    )
    client.create_index(index_name, body)
    print(f"\n인덱스 '{index_name}' 생성 완료")

    # 문서 인덱싱
    documents = [
        "빵은 밀가루로 만든 음식입니다.",
        "파이썬은 프로그래밍 언어입니다.",
        "OpenSearch는 검색 엔진입니다.",
        "케이크는 달콤한 디저트입니다.",
    ]

    # 배치 임베딩
    embeddings = embedder.embed_batch(documents)

    # 인덱싱
    for i, (text, embedding) in enumerate(zip(documents, embeddings, strict=True)):
        client.index_document(
            index_name, {"text": text, "embedding": embedding}, doc_id=f"doc-{i}"
        )

    client.refresh(index_name)
    print(f"{len(documents)}개 문서 인덱싱 완료")

    # 시맨틱 검색
    search_query = "밀가루로 만드는 것"
    print(f"\n=== 시맨틱 검색: '{search_query}' ===")

    # 쿼리 벡터 생성
    query_vector = embedder.embed(search_query)

    # k-NN 검색
    query = KNNSearch.knn_query(field="embedding", vector=query_vector, k=3)
    body = KNNSearch.build_search_body(query, size=3)

    result = client.search(index_name, body)

    print("\n검색 결과:")
    for i, hit in enumerate(result["hits"]["hits"], 1):
        print(f"  {i}. {hit['_source']['text']}")
        print(f"     점수: {hit['_score']:.4f}")

    # 정리
    client.delete_index(index_name)
    print(f"\n인덱스 '{index_name}' 삭제 완료")


def main():
    print("=== FastEmbed 예제 ===\n")
    embedder = example_with_fastembed()

    if embedder:
        semantic_search_example(embedder)

    print("\n" + "=" * 50 + "\n")

    print("=== OpenAI 예제 ===\n")
    embedder = example_with_openai()

    if embedder:
        semantic_search_example(embedder)


if __name__ == "__main__":
    main()
