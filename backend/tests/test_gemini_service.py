import pytest
from unittest.mock import patch, MagicMock
from models.incident import IncidentSeverity, IncidentStatus


@pytest.fixture
def mock_incident():
    class MockInc:
        id = "inc-test-123"
        title = "Test Incident"
        severity = IncidentSeverity.HIGH
        affected_service = "AuthService"
        start_time = None
        status = IncidentStatus.OPEN
    return MockInc()


@patch('services.gemini_service.genai.Client')
def test_summarize_incident_returns_string(mock_client_cls, mock_incident):
    """Gemini responds successfully — returns the model text."""
    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "This is a mock summary."
    mock_client.models.generate_content.return_value = mock_response

    with patch('services.gemini_service.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = 'fake_key'
        from services.gemini_service import GeminiService
        service = GeminiService()
        result = service.summarize_incident(mock_incident, [])
    assert isinstance(result, str)
    assert len(result) > 0


def test_fallback_when_api_key_missing(mock_incident):
    """No API key → falls back gracefully without raising."""
    with patch('services.gemini_service.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = None
        from services.gemini_service import GeminiService
        service = GeminiService()
        result = service.summarize_incident(mock_incident, [])
    assert isinstance(result, str)
    # Should be some fallback/error text, not an exception
    assert len(result) > 0


@patch('services.gemini_service.genai.Client')
def test_retry_on_failure(mock_client_cls, mock_incident):
    """The decorator retries up to 3 times on exception, then succeeds."""
    import importlib
    import services.gemini_service as gem_mod

    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "Success after retry"
    mock_client.models.generate_content.side_effect = [
        Exception("Fail 1"),
        Exception("Fail 2"),
        mock_response,
    ]

    with patch('services.gemini_service.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = 'fake_key'
        with patch('time.sleep', return_value=None):
            service = gem_mod.GeminiService()
            # clear the in-memory cache so this unique id is not cached
            gem_mod._cache.clear()
            result = service.summarize_incident(mock_incident, [])

    assert "Success after retry" in result
    assert mock_client.models.generate_content.call_count == 3


@patch('services.gemini_service.genai.Client')
def test_rate_limit_respected(mock_client_cls):
    """Token bucket causes sleep when exhausted (>10 requests without pause)."""
    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "OK"
    mock_client.models.generate_content.return_value = mock_response

    with patch('services.gemini_service.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = 'fake_key'
        with patch('time.sleep', return_value=None) as mock_sleep:
            # Drain all 10 tokens then force waits
            from services.gemini_service import GeminiService, _tokens
            import services.gemini_service as gem_mod
            gem_mod._tokens = 0  # Force empty bucket → sleep on next call

            class FreshInc:
                def __init__(self, idx):
                    self.id = f"rate-test-{idx}"
                    self.title = "T"
                    self.severity = IncidentSeverity.HIGH
                    self.affected_service = "S"
                    self.start_time = None

            service = GeminiService()
            service.summarize_incident(FreshInc(999), [])
            assert mock_sleep.called
