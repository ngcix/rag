import pytest
from rag.utils.logcat import Log

def test_log_import():
    """Verify that Log class is importable and functional"""
    try:
        Log.i("TEST", "Testing logcat import")
        assert True
    except Exception as e:
        pytest.fail(f"Log import failed: {e}")

def test_config_import():
    """Verify that config is importable"""
    from rag.utils.config import getConfig
    config = getConfig()
    assert config is not None
