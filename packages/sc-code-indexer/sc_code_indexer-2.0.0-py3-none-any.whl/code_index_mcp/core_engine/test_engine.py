import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from .engine import CoreEngine
from .types import SearchOptions, SearchResponse, ChunkType

@pytest.fixture
def mock_vector_backend():
    with patch('code_index_mcp.core_engine.engine.VectorBackend') as MockBackend:
        backend_instance = MockBackend.return_value
        backend_instance.search = AsyncMock(return_value=SearchResponse(data=[]))
        backend_instance.upload_file = AsyncMock()
        backend_instance.delete_file = AsyncMock()
        backend_instance.client = MagicMock() # Simulate connected client
        yield backend_instance

@pytest.fixture
def mock_legacy_backend():
    mock = MagicMock()
    mock.search.search_files = MagicMock(return_value=[])
    mock.storage.save_file_content = MagicMock()
    mock.search.index_file = MagicMock()
    mock.metadata.save_file_metadata = MagicMock()
    return mock

@pytest.mark.asyncio
async def test_search_routing_vector_primary(mock_vector_backend, mock_legacy_backend):
    engine = CoreEngine(api_key="test", legacy_backend=mock_legacy_backend)
    
    # Mock VectorBackend response
    mock_vector_backend.search.return_value = SearchResponse(data=[
        ChunkType(type="text", text="vector result", score=0.9)
    ])
    
    results = await engine.search(["store1"], "query")
    
    assert len(results.data) == 1
    assert results.data[0].text == "vector result"
    mock_vector_backend.search.assert_called_once()
    # Legacy should NOT be called if Vector succeeds (based on current logic falling through only on error/empty? No, logic is Priority 3 returns)
    mock_legacy_backend.search.search_files.assert_not_called()

@pytest.mark.asyncio
async def test_search_fallback_legacy(mock_vector_backend, mock_legacy_backend):
    engine = CoreEngine(api_key="test", legacy_backend=mock_legacy_backend)
    
    # Mock VectorBackend failure
    mock_vector_backend.client = None # Simulate no client/failure
    
    # Mock Legacy response
    mock_legacy_backend.search.search_files.return_value = [
        {"content": "legacy result", "score": 0.5, "file_path": "test.py"}
    ]
    
    results = await engine.search(["store1"], "query")
    
    assert len(results.data) == 1
    assert results.data[0].text == "legacy result"
    mock_legacy_backend.search.search_files.assert_called_once()

@pytest.mark.asyncio
async def test_index_file_dual_write(mock_vector_backend, mock_legacy_backend):
    engine = CoreEngine(api_key="test", legacy_backend=mock_legacy_backend)
    
    await engine.index_file("store1", "test.py", "content")
    
    mock_vector_backend.upload_file.assert_called_once()
    mock_legacy_backend.storage.save_file_content.assert_called_once()
    mock_legacy_backend.search.index_file.assert_called_once()
