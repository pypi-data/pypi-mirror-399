"""
VectorStore 래퍼 클래스

간단한 인터페이스로 벡터 저장/검색 제공
"""

import contextlib
import logging
from dataclasses import dataclass
from typing import Any

from opensearchpy.exceptions import NotFoundError, RequestError

from opensearch_client.client import OpenSearchClient
from opensearch_client.index import IndexManager
from opensearch_client.semantic_search.embeddings.base import BaseEmbedding

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """검색 결과"""

    text: str
    score: float
    metadata: dict[str, Any]
    id: str


class VectorStore:
    """
    벡터스토어 래퍼 클래스

    텍스트를 자동으로 임베딩하여 저장하고 검색하는 간단한 인터페이스 제공

    Example:
        ```python
        from opensearch_client import OpenSearchClient, VectorStore
        from opensearch_client.semantic_search.embeddings import FastEmbedEmbedding

        client = OpenSearchClient(host="localhost", port=9200, use_ssl=False)
        embedder = FastEmbedEmbedding()

        store = VectorStore("my-docs", embedder, client)
        store.add(["문서1", "문서2", "문서3"])

        results = store.search("검색어", k=5)
        for r in results:
            print(f"{r.score:.3f}: {r.text}")
        ```
    """

    def __init__(
        self,
        index_name: str,
        embedder: BaseEmbedding,
        client: OpenSearchClient,
        text_field: str = "content",
        vector_field: str = "embedding",
        use_korean_analyzer: bool = True,
        auto_create: bool = True,
    ):
        """
        VectorStore 초기화

        Args:
            index_name: 인덱스 이름
            embedder: 임베딩 모델 (FastEmbedEmbedding, OpenAIEmbedding 등)
            client: OpenSearchClient 인스턴스
            text_field: 텍스트 필드명
            vector_field: 벡터 필드명
            use_korean_analyzer: 한국어 Nori 분석기 사용 여부
            auto_create: 인덱스 자동 생성 여부
        """
        self.index_name = index_name
        self.embedder = embedder
        self.client = client
        self.text_field = text_field
        self.vector_field = vector_field
        self.use_korean_analyzer = use_korean_analyzer
        self._pipeline_id = f"{index_name}-pipeline"

        if auto_create:
            self._ensure_index()

    def _ensure_index(self) -> None:
        """인덱스와 파이프라인이 없으면 생성"""
        if not self.client.index_exists(self.index_name):
            body = IndexManager.create_hybrid_index_body(
                text_fields={self.text_field: "text"},
                vector_field=self.vector_field,
                vector_dimension=self.embedder.dimension,
                use_korean_analyzer=self.use_korean_analyzer,
            )
            self.client.create_index(self.index_name, body)

        # 파이프라인 생성 (이미 있으면 무시)
        try:
            self.client.setup_hybrid_pipeline(
                pipeline_id=self._pipeline_id, text_weight=0.3, vector_weight=0.7
            )
        except RequestError as e:
            # 리소스 이미 존재하는 경우만 무시
            if "resource_already_exists" not in str(e).lower():
                logger.warning("Failed to setup hybrid pipeline: %s", e)
                raise

    def add(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        텍스트 추가 (자동 임베딩)

        Args:
            texts: 저장할 텍스트 리스트
            metadata: 각 텍스트의 메타데이터 리스트 (선택)
            ids: 문서 ID 리스트 (선택, 없으면 자동 생성)

        Returns:
            저장된 문서 ID 리스트
        """
        if not texts:
            return []

        if metadata is None:
            metadata = [{}] * len(texts)

        if len(metadata) != len(texts):
            raise ValueError("texts와 metadata 길이가 다릅니다")

        if ids is not None and len(ids) != len(texts):
            raise ValueError("texts와 ids 길이가 다릅니다")

        # 배치 임베딩으로 성능 개선
        vectors = self.embedder.embed_batch(texts)

        # 문서 생성
        documents = []
        for i, (text, vector) in enumerate(zip(texts, vectors, strict=True)):
            doc = {
                self.text_field: text,
                self.vector_field: vector,
                **metadata[i],
            }
            if ids:
                doc["_id"] = ids[i]
            documents.append(doc)

        # bulk_index 사용
        id_field = "_id" if ids else None
        result = self.client.bulk_index(self.index_name, documents, id_field=id_field)

        # 결과에서 문서 ID 추출
        doc_ids = []
        for item in result.get("items", []):
            index_result = item.get("index", {})
            doc_ids.append(index_result.get("_id", ""))

        self.client.refresh(self.index_name)
        return doc_ids

    def add_one(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        """
        단일 텍스트 추가

        Args:
            text: 저장할 텍스트
            metadata: 메타데이터 (선택)
            doc_id: 문서 ID (선택)

        Returns:
            저장된 문서 ID
        """
        ids = self.add(
            [text], [metadata] if metadata else None, [doc_id] if doc_id else None
        )
        return ids[0]

    def search(
        self, query: str, k: int = 5, filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """
        유사도 검색

        Args:
            query: 검색 쿼리
            k: 반환할 결과 수
            filter: 필터 조건 (선택)

        Returns:
            SearchResult 리스트
        """
        results = self.client.hybrid_search(
            index_name=self.index_name,
            query=query,
            query_vector=self.embedder.embed(query),
            pipeline=self._pipeline_id,
            text_fields=[self.text_field],
            vector_field=self.vector_field,
            k=k,
            size=k,
            filter=filter,
        )

        return [
            SearchResult(
                text=hit["_source"].get(self.text_field, ""),
                score=hit["_score"],
                metadata={
                    k: v
                    for k, v in hit["_source"].items()
                    if k not in (self.text_field, self.vector_field)
                },
                id=hit["_id"],
            )
            for hit in results["hits"]["hits"]
        ]

    def delete(self, ids: list[str]) -> None:
        """
        문서 삭제

        Args:
            ids: 삭제할 문서 ID 리스트
        """
        for doc_id in ids:
            with contextlib.suppress(NotFoundError):
                self.client.delete_document(self.index_name, doc_id)
        self.client.refresh(self.index_name)

    def clear(self) -> None:
        """모든 문서 삭제 (인덱스 재생성)"""
        if self.client.index_exists(self.index_name):
            self.client.delete_index(self.index_name)
        self._ensure_index()

    def count(self) -> int:
        """저장된 문서 수 반환"""
        result = self.client.search(
            self.index_name, {"query": {"match_all": {}}, "size": 0}
        )
        return result["hits"]["total"]["value"]
