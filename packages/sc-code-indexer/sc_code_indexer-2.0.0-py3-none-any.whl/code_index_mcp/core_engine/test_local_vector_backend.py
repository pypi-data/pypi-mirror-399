"""
Test suite for LocalVectorBackend.

Basic tests to verify the implementation works correctly.
"""

import asyncio
import os
import tempfile
import shutil
import pytest

from .local_vector_backend import (
    LocalVectorBackend,
    get_local_vector_backend_status,
    SUPPORTED_MODELS,
    DEFAULT_MODEL
)
from .types import SearchOptions, UploadFileOptions, FileMetadata


class TestLocalVectorBackendStatus:
    """Test dependency status checking."""

    def test_status_function_exists(self):
        """Test that status function returns expected structure."""
        status = get_local_vector_backend_status()
        assert isinstance(status, dict)
        assert "available" in status
        assert "faiss_available" in status
        assert "sentence_transformers_available" in status
        assert "numpy_available" in status
        assert "supported_models" in status

    def test_supported_models_configured(self):
        """Test that supported models are properly configured."""
        assert "BAAI/bge-small-en-v1.5" in SUPPORTED_MODELS
        assert "microsoft/codebert-base" in SUPPORTED_MODELS
        assert "all-MiniLM-L6-v2" in SUPPORTED_MODELS

        # Check config structure
        for model, config in SUPPORTED_MODELS.items():
            assert "dim" in config
            assert "size_mb" in config
            assert "description" in config
            assert isinstance(config["dim"], int)


class TestLocalVectorBackendInit:
    """Test LocalVectorBackend initialization."""

    @pytest.fixture
    def temp_index_path(self):
        """Create a temporary directory for index files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_init_with_defaults(self, temp_index_path):
        """Test initialization with default parameters."""
        backend = LocalVectorBackend(index_path=temp_index_path)
        assert backend.model_name == DEFAULT_MODEL
        assert backend.index_path == temp_index_path
        assert backend.index_threshold == 100000
        assert backend.dimension == SUPPORTED_MODELS[DEFAULT_MODEL]["dim"]

    def test_init_with_custom_model(self, temp_index_path):
        """Test initialization with custom model."""
        backend = LocalVectorBackend(
            model_name="all-MiniLM-L6-v2",
            index_path=temp_index_path
        )
        assert backend.model_name == "all-MiniLM-L6-v2"
        assert backend.dimension == SUPPORTED_MODELS["all-MiniLM-L6-v2"]["dim"]

    def test_init_with_unknown_model(self, temp_index_path):
        """Test initialization with unknown model falls back to default."""
        backend = LocalVectorBackend(
            model_name="unknown/model",
            index_path=temp_index_path
        )
        # Should fall back to default
        assert backend.model_name == DEFAULT_MODEL

    def test_is_available_without_init(self, temp_index_path):
        """Test that backend is not available before initialization."""
        backend = LocalVectorBackend(index_path=temp_index_path)
        assert not backend.is_available()


@pytest.mark.integration
class TestLocalVectorBackendIntegration:
    """Integration tests that require dependencies."""

    @pytest.fixture
    async def backend(self):
        """Create an initialized backend for testing."""
        temp_dir = tempfile.mkdtemp()
        backend = LocalVectorBackend(index_path=temp_dir)

        # Skip if dependencies not available
        status = get_local_vector_backend_status()
        if not status["available"]:
            pytest.skip(f"Dependencies not available: {status['install_command']}")

        await backend.initialize()
        yield backend

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_initialize(self, backend):
        """Test successful initialization."""
        assert backend.is_available()
        assert backend._index is not None
        assert backend._index_metadata is not None

    @pytest.mark.asyncio
    async def test_create_store(self, backend):
        """Test store creation."""
        result = await backend.create_store("test_store", "Test store description")
        assert result["name"] == "test_store"
        assert result["description"] == "Test store description"

    @pytest.mark.asyncio
    async def test_upload_and_search(self, backend):
        """Test file upload and search."""
        # Upload a test file
        content = """
def hello_world():
    '''A simple hello world function.'''
    print("Hello, World!")

class MyClass:
    '''A simple test class.'''
    def __init__(self):
        self.value = 42
"""

        await backend.upload_file(
            store_id="test_store",
            file_path="test.py",
            content=content,
            options=UploadFileOptions(external_id="test.py")
        )

        # Search
        results = await backend.search(
            store_ids=["test_store"],
            query="hello world function",
            options=SearchOptions(top_k=5)
        )

        assert len(results.data) > 0
        assert results.data[0].type == "text"
        assert results.data[0].score > 0

    @pytest.mark.asyncio
    async def test_get_info(self, backend):
        """Test getting store info."""
        # Upload a file first
        await backend.upload_file(
            store_id="test_store",
            file_path="test.py",
            content="print('test')",
            options=UploadFileOptions(external_id="test.py")
        )

        # Get info
        info = await backend.get_info("test_store")
        assert info.name == "test_store"
        assert info.counts["vectors"] > 0

    @pytest.mark.asyncio
    async def test_list_files(self, backend):
        """Test listing files."""
        # Upload files
        await backend.upload_file(
            store_id="test_store",
            file_path="test1.py",
            content="print('test1')",
            options=UploadFileOptions(external_id="test1.py")
        )
        await backend.upload_file(
            store_id="test_store",
            file_path="test2.py",
            content="print('test2')",
            options=UploadFileOptions(external_id="test2.py")
        )

        # List files
        files = []
        async for f in backend.list_files("test_store"):
            files.append(f)

        assert len(files) >= 2
        paths = {f.metadata.path for f in files}
        assert any("test1.py" in p for p in paths)
        assert any("test2.py" in p for p in paths)

    @pytest.mark.asyncio
    async def test_index_persistence(self, backend):
        """Test that index persists across restarts."""
        # Upload a file
        await backend.upload_file(
            store_id="test_store",
            file_path="test.py",
            content="print('test')",
            options=UploadFileOptions(external_id="test.py")
        )

        # Save index
        backend._save_index()

        # Create new backend with same path
        backend2 = LocalVectorBackend(index_path=backend.index_path)
        await backend2.initialize()

        # Should have loaded the existing index
        assert backend2._index_metadata.vector_count > 0

    @pytest.mark.asyncio
    async def test_clear_index(self, backend):
        """Test clearing the index."""
        # Upload a file
        await backend.upload_file(
            store_id="test_store",
            file_path="test.py",
            content="print('test')",
            options=UploadFileOptions(external_id="test.py")
        )

        # Clear index
        backend.clear_index()

        # Index should be empty
        assert backend._index_metadata.vector_count == 0
        assert backend._index.ntotal == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
