import pytest
from core.engine import Rush
from core.security import SecurityEngine
import time

def test_connection():
    rush = Rush()
    result = rush.connect("test_source", {"key": "value"})
    assert "Connected" in result
    assert "test_source" in rush.registry

def test_retrieval():
    rush = Rush()
    rush.connect("test_source", {"key": "value"})
    data = rush.get("test_source")
    assert data == {"key": "value"}

def test_rate_limit():
    security = SecurityEngine()
    ip = "127.0.0.1"
    
    # Should pass 60 times
    for _ in range(60):
        assert security.check_limit(ip) is True
        
    # Should fail on 61st
    with pytest.raises(Exception) as excinfo:
        security.check_limit(ip)
    assert "429" in str(excinfo.value)
