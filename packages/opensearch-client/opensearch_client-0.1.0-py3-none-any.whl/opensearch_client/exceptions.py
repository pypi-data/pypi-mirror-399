"""
OpenSearch Client 커스텀 예외

라이브러리 전용 예외 클래스 정의
"""

from typing import Any


class OpenSearchClientError(Exception):
    """OpenSearch Client 기본 예외"""

    pass


class BulkIndexError(OpenSearchClientError):
    """
    벌크 인덱싱 부분 실패 예외

    bulk_index 작업에서 일부 문서 인덱싱이 실패한 경우 발생
    """

    def __init__(self, message: str, failed_items: list[dict[str, Any]]):
        """
        Args:
            message: 에러 메시지
            failed_items: 실패한 문서 목록 (각 항목에 error 정보 포함)
        """
        super().__init__(message)
        self.failed_items = failed_items
        self.failed_count = len(failed_items)

    def __str__(self) -> str:
        return f"{self.args[0]} (failed: {self.failed_count} documents)"
