# Testing Guide

이 문서는 opensearch-client 프로젝트의 테스트 및 CI/CD 관련 가이드입니다.

## 테스트 구조

```
tests/
├── unit/                    # 단위 테스트 (OpenSearch 불필요)
│   ├── test_analyzer.py     # 텍스트 분석기 테스트
│   ├── test_client_unit.py  # OpenSearchClient 모킹 테스트
│   ├── test_embeddings.py   # 임베딩 제공자 테스트
│   ├── test_index.py        # IndexManager 테스트
│   └── ...
├── integration/             # 통합 테스트 (OpenSearch 필요)
│   ├── test_client.py
│   └── test_hybrid_search.py
└── conftest.py              # 공통 fixture
```

## 테스트 실행

### 단위 테스트

```bash
# 전체 단위 테스트
uv run pytest tests/unit -v

# 특정 파일
uv run pytest tests/unit/test_client_unit.py -v

# 특정 테스트
uv run pytest tests/unit/test_client_unit.py::TestOpenSearchClientInit -v
```

### 통합 테스트

```bash
# OpenSearch 실행 (포트 9201)
docker compose -f docker-compose.test.yml up -d

# 통합 테스트 실행
uv run pytest tests/integration -v

# 종료
docker compose -f docker-compose.test.yml down
```

### 커버리지 측정

```bash
# 커버리지 리포트 (터미널)
uv run pytest tests/unit -v --cov=opensearch_client --cov-report=term-missing

# HTML 리포트 생성
uv run pytest --cov=opensearch_client --cov-report=html
# htmlcov/index.html 에서 확인
```

## 커버리지 요구사항

- **최소 커버리지: 70%**
- CI에서 자동으로 검사 (`--cov-fail-under=70`)
- 현재 커버리지: 약 94%

## CI/CD 파이프라인

### GitHub Actions 워크플로우

`.github/workflows/ci.yml`에서 다음 작업을 수행합니다:

| Job | 설명 |
|-----|------|
| `lint` | Ruff 린트, 포맷 검사, ty 타입 체크 |
| `test` | Python 3.10, 3.11, 3.12에서 단위 테스트 |
| `test-report` | JUnit XML 리포트를 GitHub UI에 표시 |
| `integration` | Docker로 OpenSearch 실행 후 통합 테스트 |

### Codecov 연동

- 커버리지 리포트가 자동으로 [Codecov](https://codecov.io/gh/namyoungkim/opensearch-client)에 업로드됩니다
- PR에서 커버리지 변화를 확인할 수 있습니다
- README에 커버리지 배지가 표시됩니다

### JUnit 테스트 리포트

- `dorny/test-reporter`를 사용하여 테스트 결과를 GitHub Actions UI에 표시
- 실패한 테스트를 빠르게 확인할 수 있습니다

## 테스트 작성 가이드

### Mock 사용

`tests/conftest.py`에 공통 Mock이 정의되어 있습니다:

```python
# MockEmbedder 사용 예시
def test_with_mock_embedder(mock_embedder):
    # mock_embedder는 384차원 고정 벡터 반환
    vector = mock_embedder.embed("test")
    assert len(vector) == 384
```

### 단위 테스트 패턴

OpenSearch 의존성 없이 테스트하려면 `unittest.mock`을 사용:

```python
from unittest.mock import MagicMock, patch

def test_client_method():
    with patch("opensearch_client.client.OpenSearch") as mock_os:
        mock_os.return_value.ping.return_value = True
        client = OpenSearchClient()
        assert client.ping() is True
```

### 통합 테스트 마커

OpenSearch가 필요한 테스트는 마커를 사용:

```python
import pytest

@pytest.mark.integration
def test_real_opensearch(opensearch_client):
    assert opensearch_client.ping()
```

## 로컬 개발 팁

### 테스트 포트 변경

```bash
# 환경 변수로 포트 변경
OPENSEARCH_TEST_PORT=9202 uv run pytest tests/integration -v
```

### 특정 테스트만 실행

```bash
# 키워드로 필터링
uv run pytest -k "hybrid" -v

# 마커로 필터링
uv run pytest -m "not integration" -v
```

---

*Last Updated: 2025-12-31*
