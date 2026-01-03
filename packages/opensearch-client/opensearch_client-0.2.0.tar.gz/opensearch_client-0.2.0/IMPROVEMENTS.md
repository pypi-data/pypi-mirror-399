# OpenSearch Client 개선 사항

코드 리뷰를 통해 발견된 개선 사항들을 정리한 문서입니다.

---

## 1. 성능 개선

### 1.1 VectorStore.add()에서 배치 임베딩 활용 ✅ 완료

**파일**: `src/opensearch_client/vectorstore.py:125-132`

**현재 코드**:
```python
for i, text in enumerate(texts):
    doc = {
        self.text_field: text,
        self.vector_field: self.embedder.embed(text),  # 개별 호출
        ...
    }
```

**문제점**:
- 텍스트마다 개별 `embed()` 호출
- OpenAI API 사용 시 요청 수 증가로 비용 상승
- 네트워크 오버헤드로 인한 성능 저하

**개선 방안**:
```python
def add(self, texts: List[str], ...) -> List[str]:
    vectors = self.embedder.embed_batch(texts)  # 배치 처리

    documents = []
    for i, (text, vector) in enumerate(zip(texts, vectors)):
        doc = {
            self.text_field: text,
            self.vector_field: vector,
            **metadata[i]
        }
        documents.append(doc)

    # bulk_index 활용 검토
    ...
```

**우선순위**: 높음

---

## 2. 에러 처리 개선

### 2.1 파이프라인 생성 시 예외 처리 세분화 ✅ 완료

**파일**: `src/opensearch_client/vectorstore.py:92-99`

**현재 코드**:
```python
try:
    self.client.setup_hybrid_pipeline(...)
except Exception:
    pass  # 이미 존재하는 경우 무시
```

**문제점**:
- 모든 예외를 무시하여 실제 오류 감지 불가
- 권한 오류, 네트워크 오류 등도 무시됨

**개선 방안**:
```python
from opensearchpy.exceptions import RequestError

try:
    self.client.setup_hybrid_pipeline(...)
except RequestError as e:
    # 리소스 이미 존재하는 경우만 무시
    if "resource_already_exists" not in str(e).lower():
        raise
except Exception as e:
    # 예상치 못한 오류는 로깅 후 재발생
    logger.warning(f"Failed to setup pipeline: {e}")
    raise
```

**우선순위**: 높음

---

### 2.2 문서 삭제 시 예외 처리 개선 ✅ 완료

**파일**: `src/opensearch_client/vectorstore.py:207-211`

**현재 코드**:
```python
for doc_id in ids:
    try:
        self.client.delete_document(self.index_name, doc_id)
    except Exception:
        pass  # 이미 없는 경우 무시
```

**개선 방안**:
```python
from opensearchpy.exceptions import NotFoundError

for doc_id in ids:
    try:
        self.client.delete_document(self.index_name, doc_id)
    except NotFoundError:
        pass  # 문서가 없는 경우만 무시
```

**우선순위**: 중간

---

### 2.3 bulk_index 결과 검증 ✅ 완료

**파일**: `src/opensearch_client/client.py:142-150`

**현재 코드**:
```python
def bulk_index(...) -> Dict[str, Any]:
    ...
    return self._client.bulk(body=actions)
```

**문제점**:
- bulk 작업은 부분 실패가 가능
- `errors` 필드를 확인하지 않음

**개선 방안**:
```python
def bulk_index(..., raise_on_error: bool = True) -> Dict[str, Any]:
    ...
    result = self._client.bulk(body=actions)

    if raise_on_error and result.get("errors"):
        failed_items = [
            item for item in result["items"]
            if "error" in item.get("index", {})
        ]
        raise BulkIndexError(f"Failed to index {len(failed_items)} documents", failed_items)

    return result
```

**우선순위**: 중간

---

## 3. 코드 정리

### 3.1 미사용 파라미터 제거 또는 구현 ✅ 완료

**파일**: `src/opensearch_client/index.py:91-116`

**현재 코드**:
```python
@staticmethod
def get_knn_index_settings(
    vector_dimension: int = 1536,  # 미사용
    space_type: str = "cosinesimil",  # 미사용
    engine: str = "lucene",  # 미사용
    ef_construction: int = 128,  # 미사용
    m: int = 16  # 미사용
) -> Dict[str, Any]:
    return {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 100
        }
    }
```

**개선 방안**: 파라미터를 실제로 활용하거나, 사용하지 않는 파라미터 제거

```python
@staticmethod
def get_knn_index_settings(ef_search: int = 100) -> Dict[str, Any]:
    return {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": ef_search
        }
    }
```

**우선순위**: 낮음

---

### 3.2 미사용 의존성 제거 ✅ 완료

**파일**: `pyproject.toml:22`

**현재 코드**:
```toml
dependencies = [
    "opensearch-py>=3.0.0",
    "pydantic>=2.0",  # 실제 코드에서 사용되지 않음
]
```

**문제점**:
- `pydantic`이 의존성에 있지만 코드에서 사용하지 않음
- `dataclass`만 사용 중 (`SearchResult`)

**개선 방안**:
- pydantic을 실제로 활용하거나 의존성에서 제거
- 활용 시 `SearchResult`를 Pydantic 모델로 변환하여 유효성 검사 추가

**우선순위**: 낮음

---

### 3.3 미사용 import 제거 ✅ 완료 (이미 정리됨)

**파일**: `src/opensearch_client/hybrid_search/hybrid_query.py:7`

```python
from typing import Any, Dict, List, Optional, Union  # Union 미사용
```

**우선순위**: 낮음

---

### 3.4 Python 빌트인 섀도잉 수정 ✅ 완료

**파일**: `src/opensearch_client/vectorstore.py:143`

**현재 코드**:
```python
def add_one(
    self,
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    id: Optional[str] = None  # Python 빌트인 id 섀도잉
) -> str:
```

**개선 방안**:
```python
def add_one(
    self,
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    doc_id: Optional[str] = None  # 명확한 이름 사용
) -> str:
```

**우선순위**: 낮음

---

## 4. 기능 개선

### 4.1 korean_search_query() 필드명 파라미터화 ✅ 완료

**파일**: `src/opensearch_client/text_search/query_builder.py:170-240`

**현재 코드**:
```python
@classmethod
def korean_search_query(
    cls,
    query: str,
    ...
) -> Dict[str, Any]:
    should_clauses = [
        cls.multi_match(
            ...
            fields=["question", "answer"],  # 하드코딩
            ...
        ),
        ...
    ]
```

**문제점**:
- 필드명이 하드코딩되어 재사용성 저하
- "question", "answer" 외의 필드 구조에서 사용 불가

**개선 방안**:
```python
@classmethod
def korean_search_query(
    cls,
    query: str,
    primary_field: str = "question",
    secondary_field: str = "answer",
    ...
) -> Dict[str, Any]:
```

**우선순위**: 중간

---

### 4.2 비동기 지원 추가 ✅ 완료

**현재 상태**:
- `opensearch-py`는 `AsyncOpenSearch` 지원
- `pytest-asyncio`가 dev-dependency에 있지만 미사용
- 현재 동기 방식만 지원

**개선 방안**:
```python
# async_client.py
from opensearchpy import AsyncOpenSearch

class AsyncOpenSearchClient:
    async def search(self, index_name: str, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return await self._client.search(index=index_name, body=body, **kwargs)

    async def hybrid_search(self, ...) -> Dict[str, Any]:
        ...
```

**우선순위**: 낮음 (향후 기능)

---

## 5. 보안 개선

### 5.1 SSL 인증서 검증 기본값 변경 고려 ✅ 완료 (문서화)

**파일**: `src/opensearch_client/client.py:25`

**현재 코드**:
```python
def __init__(
    ...
    verify_certs: bool = False,  # 기본값이 False
    ...
):
```

**문제점**:
- 프로덕션 환경에서 MITM 공격에 취약
- 개발 편의를 위한 설정이 기본값

**개선 방안**:
- 문서에 프로덕션 환경에서는 `verify_certs=True` 사용 권장 명시
- 또는 기본값을 `True`로 변경하고 개발 환경 가이드 제공

**우선순위**: 중간

---

## 6. 테스트 개선

### 6.1 에러 케이스 테스트 추가 ✅ 완료

**현재 상태**:
- Happy path 테스트 위주
- 에러 상황 테스트 부족

**추가 필요 테스트**:
- 네트워크 오류 시 동작
- 잘못된 벡터 차원 처리
- 인덱스 생성 실패 시 동작
- bulk_index 부분 실패 처리

**우선순위**: 중간

---

## 우선순위 요약

| 우선순위 | 항목 |
|---------|------|
| **높음** | ~~배치 임베딩 활용~~ ✅, ~~예외 처리 세분화~~ ✅ |
| **중간** | ~~bulk_index 검증~~ ✅, ~~필드명 파라미터화~~ ✅, ~~SSL 문서화~~ ✅, ~~테스트 추가~~ ✅ |
| **낮음** | ~~미사용 코드 정리~~ ✅, ~~비동기 지원~~ ✅ |

---

## 변경 이력

| 날짜 | 작성자 | 내용 |
|------|--------|------|
| 2025-12-31 | Claude Code | 초기 작성 |
| 2025-12-31 | Claude Code | 고우선순위 항목 구현 완료 (1.1, 2.1, 2.2) |
| 2025-12-31 | Claude Code | 중간 우선순위 항목 구현 완료 (2.3, 4.1, 5.1, 6.1) |
| 2025-12-31 | Claude Code | 낮은 우선순위 항목 구현 완료 (3.1-3.4, 4.2) - 모든 개선 완료 🎉 |
