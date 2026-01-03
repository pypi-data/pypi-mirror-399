"""
임베딩 모듈

다양한 임베딩 모델 지원 (OpenAI, FastEmbed 등)
"""

from opensearch_client.semantic_search.embeddings.base import BaseEmbedding

# 선택적 임포트 (설치된 경우에만)
__all__ = ["BaseEmbedding"]

try:
    from opensearch_client.semantic_search.embeddings.fastembed import (
        FastEmbedEmbedding,
    )

    __all__.append("FastEmbedEmbedding")
except ImportError:
    pass

try:
    from opensearch_client.semantic_search.embeddings.openai import OpenAIEmbedding

    __all__.append("OpenAIEmbedding")
except ImportError:
    pass
