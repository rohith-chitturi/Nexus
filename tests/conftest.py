import pytest

@pytest.fixture
def mock_env():
    """A mock environment fixture for future tests."""
    return {"LLM_PROVIDER": "openai"}
