"""Embeddings 유닛 테스트"""

import sys
from unittest.mock import MagicMock, patch

import pytest


# 테스트를 위한 mock numpy array
class MockNumpyArray:
    """numpy array를 모킹"""

    def __init__(self, data: list[float]):
        self._data = data

    def tolist(self) -> list[float]:
        return self._data


class TestFastEmbedEmbedding:
    """FastEmbedEmbedding 테스트"""

    def test_import_error_without_fastembed(self):
        """fastembed 미설치 시 ImportError 발생"""
        # fastembed 모듈을 sys.modules에서 제거하여 ImportError 시뮬레이션
        with patch.dict(sys.modules, {"fastembed": None}):
            # 모듈을 다시 로드하여 ImportError 발생

            # 기존 모듈 캐시 제거
            if "opensearch_client.semantic_search.embeddings.fastembed" in sys.modules:
                del sys.modules[
                    "opensearch_client.semantic_search.embeddings.fastembed"
                ]

            with pytest.raises(ImportError) as exc_info:
                from opensearch_client.semantic_search.embeddings.fastembed import (
                    FastEmbedEmbedding,
                )

                FastEmbedEmbedding()
            assert "fastembed" in str(exc_info.value).lower()

    def test_default_model_name(self):
        """기본 모델명은 BAAI/bge-small-en-v1.5"""
        # fastembed가 설치되어 있으므로 직접 테스트
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding()
            assert embedder.model_name == "BAAI/bge-small-en-v1.5"

    def test_custom_model_name(self):
        """커스텀 모델명이 적용되어야 함"""
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
            assert embedder.model_name == "BAAI/bge-base-en-v1.5"

    def test_dimension_for_small_model(self):
        """bge-small 모델의 차원은 384"""
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
            assert embedder.dimension == 384

    def test_dimension_for_base_model(self):
        """bge-base 모델의 차원은 768"""
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
            assert embedder.dimension == 768

    def test_dimension_for_large_model(self):
        """bge-large 모델의 차원은 1024"""
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")
            assert embedder.dimension == 1024

    def test_dimension_for_unknown_model(self):
        """알 수 없는 모델의 기본 차원은 384"""
        mock_text_embedding = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding(model_name="unknown/model")
            assert embedder.dimension == 384

    def test_embed_single_text(self):
        """단일 텍스트 임베딩"""
        mock_text_embedding = MagicMock()
        mock_text_embedding.embed.return_value = iter([MockNumpyArray([0.1, 0.2, 0.3])])

        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding()
            result = embedder.embed("test text")

            assert result == [0.1, 0.2, 0.3]
            mock_text_embedding.embed.assert_called_once_with(["test text"])

    def test_embed_batch(self):
        """배치 임베딩"""
        mock_text_embedding = MagicMock()
        mock_text_embedding.embed.return_value = iter(
            [
                MockNumpyArray([0.1, 0.2]),
                MockNumpyArray([0.3, 0.4]),
            ]
        )

        with patch("fastembed.TextEmbedding", return_value=mock_text_embedding):
            from opensearch_client.semantic_search.embeddings.fastembed import (
                FastEmbedEmbedding,
            )

            embedder = FastEmbedEmbedding()
            result = embedder.embed_batch(["text1", "text2"])

            assert result == [[0.1, 0.2], [0.3, 0.4]]
            mock_text_embedding.embed.assert_called_once_with(["text1", "text2"])


class TestOpenAIEmbedding:
    """OpenAIEmbedding 테스트"""

    def test_import_error_without_openai(self):
        """openai 미설치 시 ImportError 발생"""
        with patch.dict(sys.modules, {"openai": None}):
            if "opensearch_client.semantic_search.embeddings.openai" in sys.modules:
                del sys.modules["opensearch_client.semantic_search.embeddings.openai"]

            with pytest.raises(ImportError) as exc_info:
                from opensearch_client.semantic_search.embeddings.openai import (
                    OpenAIEmbedding,
                )

                OpenAIEmbedding()
            assert "openai" in str(exc_info.value).lower()

    def test_default_model_name(self):
        """기본 모델명은 text-embedding-3-small"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding()
            assert embedder.model_name == "text-embedding-3-small"

    def test_custom_model_name(self):
        """커스텀 모델명이 적용되어야 함"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(model_name="text-embedding-3-large")
            assert embedder.model_name == "text-embedding-3-large"

    def test_dimension_for_small_model(self):
        """text-embedding-3-small 모델의 차원은 1536"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(model_name="text-embedding-3-small")
            assert embedder.dimension == 1536

    def test_dimension_for_large_model(self):
        """text-embedding-3-large 모델의 차원은 3072"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(model_name="text-embedding-3-large")
            assert embedder.dimension == 3072

    def test_dimension_for_ada_model(self):
        """text-embedding-ada-002 모델의 차원은 1536"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(model_name="text-embedding-ada-002")
            assert embedder.dimension == 1536

    def test_custom_dimensions_override(self):
        """커스텀 dimensions가 기본값을 오버라이드해야 함"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(dimensions=512)
            assert embedder.dimension == 512

    def test_unknown_model_default_dimension(self):
        """알 수 없는 모델의 기본 차원은 1536"""
        mock_openai = MagicMock()
        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(model_name="unknown-model")
            assert embedder.dimension == 1536

    def test_embed_single_text(self):
        """단일 텍스트 임베딩"""
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]
        mock_openai.embeddings.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding()
            result = embedder.embed("test text")

            assert result == [0.1, 0.2, 0.3]
            mock_openai.embeddings.create.assert_called_once_with(
                input="test text", model="text-embedding-3-small"
            )

    def test_embed_with_custom_dimensions(self):
        """커스텀 dimensions로 임베딩"""
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.embedding = [0.1, 0.2]
        mock_response.data = [mock_data]
        mock_openai.embeddings.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding(dimensions=256)
            embedder.embed("test text")

            mock_openai.embeddings.create.assert_called_once_with(
                input="test text", model="text-embedding-3-small", dimensions=256
            )

    def test_embed_batch(self):
        """배치 임베딩"""
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_data1 = MagicMock()
        mock_data1.embedding = [0.1, 0.2]
        mock_data1.index = 0
        mock_data2 = MagicMock()
        mock_data2.embedding = [0.3, 0.4]
        mock_data2.index = 1
        mock_response.data = [mock_data2, mock_data1]  # 순서 섞음
        mock_openai.embeddings.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            embedder = OpenAIEmbedding()
            result = embedder.embed_batch(["text1", "text2"])

            # 인덱스 순서대로 정렬되어야 함
            assert result == [[0.1, 0.2], [0.3, 0.4]]

    def test_ada_model_without_dimensions_param(self):
        """ada 모델은 dimensions 파라미터 미지원"""
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.embedding = [0.1, 0.2]
        mock_response.data = [mock_data]
        mock_openai.embeddings.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_openai):
            from opensearch_client.semantic_search.embeddings.openai import (
                OpenAIEmbedding,
            )

            # ada 모델에 dimensions 지정해도 API 호출에는 포함 안됨
            embedder = OpenAIEmbedding(
                model_name="text-embedding-ada-002", dimensions=256
            )
            embedder.embed("test")

            # dimensions 파라미터가 없어야 함
            mock_openai.embeddings.create.assert_called_once_with(
                input="test", model="text-embedding-ada-002"
            )
