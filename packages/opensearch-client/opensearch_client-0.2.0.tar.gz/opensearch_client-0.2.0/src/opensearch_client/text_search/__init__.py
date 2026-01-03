"""
텍스트 검색 모듈

멀티매치 쿼리, 퍼지 매칭, 구문 매칭 등 텍스트 기반 검색 기능
"""

from opensearch_client.text_search.analyzer import AnalyzerConfig
from opensearch_client.text_search.query_builder import TextQueryBuilder

__all__ = ["AnalyzerConfig", "TextQueryBuilder"]
