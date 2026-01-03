"""
비동기 OpenSearch 클라이언트

AsyncOpenSearch를 래핑하여 비동기 검색 기능 제공

Note:
    비동기 클라이언트를 사용하려면 aiohttp가 설치되어 있어야 합니다:
    `uv add opensearch-client[async]` 또는 `pip install opensearch-client[async]`
"""

from typing import Any

try:
    from opensearchpy import AsyncOpenSearch
except ImportError as err:
    raise ImportError(
        "AsyncOpenSearch is not available. "
        "Install async support with: uv add opensearch-client[async]"
    ) from err


class AsyncOpenSearchClient:
    """
    비동기 OpenSearch 클라이언트 래퍼 클래스

    텍스트 검색, 시맨틱 검색, 하이브리드 검색을 위한 비동기 인터페이스 제공
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9200,
        user: str | None = None,
        password: str | None = None,
        use_ssl: bool = True,
        verify_certs: bool = False,
        **kwargs,
    ):
        """
        비동기 OpenSearch 클라이언트 초기화

        Args:
            host: OpenSearch 호스트 주소
            port: OpenSearch 포트
            user: 인증 사용자명 (선택)
            password: 인증 비밀번호 (선택)
            use_ssl: SSL 사용 여부
            verify_certs: 인증서 검증 여부
            **kwargs: 추가 OpenSearch 클라이언트 옵션

        Warning:
            보안 권장사항:
            - 프로덕션 환경에서는 반드시 verify_certs=True 사용을 권장합니다.
            - verify_certs=False는 개발/테스트 환경에서만 사용하세요.
        """
        auth = (user, password) if user and password else None

        self._client = AsyncOpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            **kwargs,
        )

    @property
    def raw_client(self) -> AsyncOpenSearch:
        """원본 AsyncOpenSearch 클라이언트 반환"""
        return self._client

    async def close(self) -> None:
        """클라이언트 연결 종료"""
        await self._client.close()

    async def __aenter__(self) -> "AsyncOpenSearchClient":
        """컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """컨텍스트 매니저 종료"""
        await self.close()

    async def ping(self) -> bool:
        """OpenSearch 연결 상태 확인"""
        return await self._client.ping()

    async def info(self) -> dict[str, Any]:
        """OpenSearch 클러스터 정보 반환"""
        return await self._client.info()

    # === 인덱스 관리 ===

    async def create_index(
        self, index_name: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """인덱스 생성"""
        return await self._client.indices.create(index=index_name, body=body or {})

    async def delete_index(self, index_name: str) -> dict[str, Any]:
        """인덱스 삭제"""
        return await self._client.indices.delete(index=index_name)

    async def index_exists(self, index_name: str) -> bool:
        """인덱스 존재 여부 확인"""
        return await self._client.indices.exists(index=index_name)

    async def refresh(self, index_name: str) -> dict[str, Any]:
        """인덱스 새로고침"""
        return await self._client.indices.refresh(index=index_name)

    # === 문서 관리 ===

    async def index_document(
        self, index_name: str, document: dict[str, Any], doc_id: str | None = None
    ) -> dict[str, Any]:
        """문서 인덱싱"""
        return await self._client.index(index=index_name, body=document, id=doc_id)

    async def bulk_index(
        self,
        index_name: str,
        documents: list[dict[str, Any]],
        id_field: str | None = None,
        raise_on_error: bool = False,
    ) -> dict[str, Any]:
        """
        벌크 인덱싱

        Args:
            index_name: 인덱스 이름
            documents: 인덱싱할 문서 리스트
            id_field: 문서 ID로 사용할 필드명 (선택)
            raise_on_error: 부분 실패 시 예외 발생 여부

        Raises:
            BulkIndexError: raise_on_error=True이고 일부 문서 인덱싱 실패 시
        """
        from opensearch_client.exceptions import BulkIndexError

        actions = []
        for doc in documents:
            action = {"index": {"_index": index_name}}
            if id_field and id_field in doc:
                action["index"]["_id"] = doc[id_field]
            actions.append(action)
            actions.append(doc)

        result = await self._client.bulk(body=actions)

        if raise_on_error and result.get("errors"):
            failed_items = [
                item
                for item in result.get("items", [])
                if "error" in item.get("index", {})
            ]
            raise BulkIndexError(
                f"Failed to index {len(failed_items)} of {len(documents)} documents",
                failed_items,
            )

        return result

    async def get_document(self, index_name: str, doc_id: str) -> dict[str, Any]:
        """문서 조회"""
        return await self._client.get(index=index_name, id=doc_id)

    async def delete_document(self, index_name: str, doc_id: str) -> dict[str, Any]:
        """문서 삭제"""
        return await self._client.delete(index=index_name, id=doc_id)

    # === 검색 ===

    async def search(
        self, index_name: str, body: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """검색 실행"""
        return await self._client.search(index=index_name, body=body, **kwargs)

    # === Search Pipeline ===

    async def create_search_pipeline(
        self, pipeline_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Search Pipeline 생성"""
        return await self._client.transport.perform_request(
            "PUT", f"/_search/pipeline/{pipeline_id}", body=body
        )

    async def delete_search_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Search Pipeline 삭제"""
        return await self._client.transport.perform_request(
            "DELETE", f"/_search/pipeline/{pipeline_id}"
        )

    async def get_search_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Search Pipeline 조회"""
        return await self._client.transport.perform_request(
            "GET", f"/_search/pipeline/{pipeline_id}"
        )

    # === 하이브리드 검색 ===

    async def hybrid_search(
        self,
        index_name: str,
        query: str,
        query_vector: list[float],
        pipeline: str,
        text_fields: list[str] | None = None,
        vector_field: str = "vector",
        k: int = 10,
        size: int = 10,
        text_boost: float = 1.0,
        vector_boost: float = 1.0,
        filter: dict[str, Any] | None = None,
        source: list[str] | None = None,
        min_score: float | None = None,
    ) -> dict[str, Any]:
        """
        하이브리드 검색 실행

        텍스트 검색과 벡터 검색을 결합하여 검색

        Args:
            index_name: 검색할 인덱스
            query: 텍스트 검색 쿼리
            query_vector: 쿼리 벡터
            pipeline: 사용할 Search Pipeline 이름
            text_fields: 텍스트 검색 필드 목록
            vector_field: 벡터 필드명
            k: k-NN 결과 수
            size: 반환할 결과 수
            text_boost: 텍스트 쿼리 boost
            vector_boost: 벡터 쿼리 boost
            filter: 필터 조건
            source: 반환할 필드 목록
            min_score: 최소 점수 임계값

        Returns:
            검색 결과
        """
        from opensearch_client.hybrid_search import HybridQueryBuilder

        body = HybridQueryBuilder.build_complete_hybrid_search(
            text_query=query,
            query_vector=query_vector,
            text_fields=text_fields,
            vector_field=vector_field,
            k=k,
            size=size,
            text_boost=text_boost,
            vector_boost=vector_boost,
            filter=filter,
            source=source,
            min_score=min_score,
        )

        return await self._client.search(
            index=index_name, body=body, params={"search_pipeline": pipeline}
        )

    async def setup_hybrid_pipeline(
        self,
        pipeline_id: str = "hybrid-pipeline",
        text_weight: float = 0.3,
        vector_weight: float = 0.7,
        use_rrf: bool = False,
    ) -> dict[str, Any]:
        """
        하이브리드 검색용 Search Pipeline 설정

        Args:
            pipeline_id: 파이프라인 ID
            text_weight: 텍스트 검색 가중치 (use_rrf=False일 때)
            vector_weight: 벡터 검색 가중치 (use_rrf=False일 때)
            use_rrf: RRF (Reciprocal Rank Fusion) 사용 여부

        Returns:
            생성 결과
        """
        from opensearch_client.hybrid_search import SearchPipelineManager

        if use_rrf:
            body = SearchPipelineManager.build_pipeline_body(
                description="Hybrid search pipeline with RRF", use_rrf=True
            )
        else:
            body = SearchPipelineManager.build_default_hybrid_pipeline(
                text_weight=text_weight, vector_weight=vector_weight
            )

        return await self.create_search_pipeline(pipeline_id, body)
