# 기술 검토 문서

작성일: 2025-12-26

---

## 1. OpenSearch 버전 검토

### 버전 현황 (2025년 12월 기준)

| 버전 | 상태 | 출시일 |
|------|------|--------|
| 3.1 | **최신 (권장)** | 2025.09 |
| 3.0 | GA | 2025 |
| 2.x | 유지보수 | 4.0 출시 시 종료 |
| 1.x | Deprecated | 2025.05 지원 종료 |

### OpenSearch 3.1 주요 기능

- **Lucene 10 통합**: 벡터 인덱싱 최적화, 인덱스 크기 감소
- **벡터 양자화**: 메모리 사용량 감소
- **Search Relevance Workbench**: 검색 품질 평가 도구
- **범위 쿼리 성능 개선**: 로그 분석, 시계열 워크로드 최적화

### 참고 자료

- [OpenSearch Version History](https://docs.opensearch.org/latest/version-history/)
- [OpenSearch 3.1 Release](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-opensearch-service-opensearch-version-3-1/)

---

## 2. 한국어 분석기 (Nori) 검토

### 현황

| 항목 | 내용 |
|------|------|
| 플러그인 | opensearch-analysis-nori |
| 최신 버전 | 3.3.0 |
| 사전 | mecab-ko-dic |
| 상태 | ✅ 한국어 분석 표준 플러그인 |

### Nori 토크나이저 특징

- 한국어 형태소 분석
- 복합어 분해 (decompound_mode: mixed, discard, none)
- 사용자 정의 사전 지원
- 품사 태깅 및 필터링

### 설정 예시

```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "korean": {
          "type": "custom",
          "tokenizer": "nori_tokenizer",
          "filter": ["nori_part_of_speech"]
        }
      },
      "tokenizer": {
        "nori_tokenizer": {
          "type": "nori_tokenizer",
          "decompound_mode": "mixed"
        }
      }
    }
  }
}
```

### 참고 자료

- [AWS Nori 플러그인 가이드](https://aws.amazon.com/ko/blogs/tech/amazon-opensearch-service-korean-nori-plugin-for-analysis/)

---

## 3. 벡터 검색 방식 검토

### OpenSearch 권장 방식 (2025년)

| 방식 | 설명 | 권장도 |
|------|------|--------|
| **Hybrid Search** | 키워드 + 시맨틱 결합 | ⭐⭐⭐ 최우선 |
| Semantic Search | 벡터 임베딩 기반 | ⭐⭐ |
| Neural Sparse | 희소 벡터 + 신경망 | ⭐⭐ |
| k-NN | 전통적 근사 최근접 | ⭐ |

### Hybrid Search 성능

- 키워드 검색 대비 **8-12% 정확도 향상**
- 자연어 검색 대비 **15% 향상**
- 레이턴시 6-8% 증가 (허용 범위)

### 구현 요소

- **Search Pipeline** (OpenSearch 2.10+)
- **Normalization Processor**: min_max, l2, RRF
- **Score Ranker Processor** (OpenSearch 2.19+)

### Hybrid Search 아키텍처

```
Query
  ├── Text Query (BM25)
  │     └── Nori Analyzer
  └── Vector Query (k-NN)
        └── Embedding Model

        ↓ Search Pipeline

Score Normalization (min_max / RRF)
        ↓
Combined Results
```

### 참고 자료

- [Hybrid Search 공식 문서](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/index/)
- [AWS Hybrid Search 블로그](https://aws.amazon.com/blogs/big-data/hybrid-search-with-amazon-opensearch-service/)
- [2025 Hybrid Search Method](https://junkangworld.com/blog/unlock-perfect-hybrid-search-in-opensearch-my-2025-method)

---

## 4. Python 패키지 검토

### 패키지 매니저

| 도구 | 속도 | 권장도 | 비고 |
|------|------|--------|------|
| **uv** | pip 대비 10-100x | ⭐⭐⭐ | 2025년 신규 표준 |
| Poetry | 느림 | ⭐⭐ | 안정적, 널리 사용 |
| pip | 기본 | ⭐ | 기본 도구 |

### OpenSearch 클라이언트

| 패키지 | 버전 | 상태 |
|--------|------|------|
| **opensearch-py** | 3.1.0 | ✅ 권장 |
| opensearch-dsl-py | - | ❌ Deprecated (opensearch-py로 통합) |
| opensearch-py-ml | 최신 | 선택 (ML 기능 필요시) |

### 비동기 HTTP 클라이언트

| 패키지 | 버전 | 용도 |
|--------|------|------|
| **aiohttp** | 3.0+ | AsyncOpenSearchClient HTTP 전송 레이어 |

**참고:** `opensearch-py`의 `AsyncOpenSearch`는 내부적으로 `aiohttp`를 사용합니다.
설치: `uv add opensearch-client[async]`

### 임베딩 라이브러리 (2025년 트렌드)

| 라이브러리 | 특징 | 권장도 | 모델 예시 |
|------------|------|--------|----------|
| **FastEmbed** | 빠름, 경량 | ⭐⭐⭐ | BAAI/bge-small-en-v1.5 |
| sentence-transformers | 널리 사용 | ⭐⭐ | all-MiniLM-L6-v2 |
| OpenAI Embeddings | API 기반 | ⭐⭐ | text-embedding-3-small |

### 임베딩 모델 비교

| 모델 | 차원 | 속도 | 비용 |
|------|------|------|------|
| FastEmbed (bge-small) | 384 | 빠름 | 무료 (로컬) |
| OpenAI text-embedding-3-small | 1536 | 중간 | API 비용 |
| OpenAI text-embedding-3-large | 3072 | 느림 | API 비용 (높음) |

### 참고 자료

- [opensearch-py PyPI](https://pypi.org/project/opensearch-py/)
- [FastEmbed PyPI](https://pypi.org/project/fastembed/)
- [uv 공식 문서](https://docs.astral.sh/uv/)

---

## 5. 배포 환경 검토

### Docker vs Kubernetes

| 항목 | Docker | Kubernetes |
|------|--------|------------|
| 용도 | 개발, 테스트, CI | 프로덕션 |
| 복잡도 | 낮음 | 높음 |
| 스케일링 | 수동 | 자동 |
| 자동 복구 | ❌ | ✅ |
| 무중단 배포 | 수동 | ✅ |
| 리소스 관리 | 제한적 | 고급 |

### 권장 전략

- **개발/테스트**: Docker Compose
- **프로덕션**: Kubernetes + OpenSearch Operator

### OpenSearch Kubernetes Operator 기능

- 자동화된 클러스터 관리
- Self-healing (노드 장애 자동 복구)
- 선언적 YAML 제어
- 무중단 롤링 업데이트
- 자동 스케일링

### Docker Compose 예시 (테스트용)

```yaml
services:
  opensearch:
    image: opensearchproject/opensearch:3.1.0
    environment:
      - discovery.type=single-node
      - plugins.security.disabled=true
    ports:
      - "9200:9200"
```

### Kubernetes 예시 (프로덕션)

```yaml
apiVersion: opensearch.opster.io/v1
kind: OpenSearchCluster
metadata:
  name: opensearch-cluster
spec:
  general:
    version: 3.1.0
  nodePools:
    - component: masters
      replicas: 3
      resources:
        requests:
          memory: "4Gi"
```

### 참고 자료

- [OpenSearch Kubernetes Operator](https://github.com/opensearch-project/opensearch-k8s-operator)
- [Helm Chart 배포 가이드](https://opensearch.org/blog/setup-multinode-cluster-kubernetes/)

---

## 6. 최종 기술 스택 결정

| 카테고리 | 선택 | 버전 | 선정 이유 |
|----------|------|------|----------|
| 패키지 매니저 | **uv** | latest | 속도 10-100x 향상 |
| OpenSearch | **OpenSearch** | 3.1.0 | Lucene 10, 벡터 최적화 |
| 한국어 분석 | **Nori** | 3.3.0 | 표준 한국어 플러그인 |
| Python 클라이언트 | **opensearch-py** | 3.1.0 | 공식 클라이언트, dsl 통합 |
| 임베딩 (로컬) | **FastEmbed** | 0.4+ | 빠름, 무료 |
| 임베딩 (API) | **OpenAI** | 1.0+ | 고품질, 간편 |
| 검색 방식 | **Hybrid Search** | - | 정확도 8-15% 향상 |
| 개발 환경 | **Docker Compose** | - | 간단한 설정 |
| 프로덕션 | **Kubernetes** | - | 자동 스케일링, 복구 |

---

## 7. 주의사항 및 권장사항

### 버전 호환성

- OpenSearch 3.x는 Python 클라이언트 3.x와 사용
- Nori 플러그인 버전은 OpenSearch 버전과 일치해야 함

### 성능 최적화

- 벡터 인덱스: ef_search 값 조정 (기본 100)
- 하이브리드 검색: 가중치 튜닝 필요 (텍스트:벡터 = 0.3:0.7 권장)
- 대용량 데이터: 샤드 수 조정 필요

### 보안

- 프로덕션에서는 SSL/TLS 활성화 필수
- 인증서 검증 활성화 권장
- API 키/비밀번호 환경 변수 사용

---

*Last Updated: 2025-12-31*
