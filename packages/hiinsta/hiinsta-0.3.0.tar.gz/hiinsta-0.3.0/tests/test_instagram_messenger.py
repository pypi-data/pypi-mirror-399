import json
import pytest
import httpx

from hiinsta.InstagramMessenger import InstagramMessenger
from hiinsta.types.exeptions import InstagramApiException


@pytest.mark.asyncio
async def test_send_text_success(monkeypatch):
    # Arrange
    messenger = InstagramMessenger(access_token="token", request_timeout=0.1)

    class DummyResponse:
        status_code = 200
        def json(self):
            return {"message_id": "m_123"}
        @property
        def text(self):
            return json.dumps(self.json())

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None):
            return DummyResponse()

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    # Act
    mid = await messenger.send_text("hello", "user_1")

    # Assert
    assert mid == "m_123"


@pytest.mark.asyncio
async def test_send_text_http_error(monkeypatch):
    messenger = InstagramMessenger(access_token="token")

    class DummyResponse:
        status_code = 400
        def json(self):
            return {"error": {"message": "Bad Request", "code": 100}}
        @property
        def text(self):
            return json.dumps(self.json())

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None):
            return DummyResponse()

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    with pytest.raises(InstagramApiException) as ei:
        await messenger.send_text("hello", "user_1")

    err = ei.value
    assert err.status_code == 400
    assert err.error_code == "100"
    assert "Bad Request" in str(err)


@pytest.mark.asyncio
async def test_send_text_network_error(monkeypatch):
    messenger = InstagramMessenger(access_token="token")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None):
            raise httpx.RequestError("boom", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    with pytest.raises(InstagramApiException) as ei:
        await messenger.send_text("hello", "user_1")

    assert "Network error" in str(ei.value)


@pytest.mark.asyncio
async def test_send_text_invalid_json(monkeypatch):
    messenger = InstagramMessenger(access_token="token")

    class DummyResponse:
        status_code = 200
        def json(self):
            raise ValueError("invalid json")
        @property
        def text(self):
            return "<not-json>"

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None):
            return DummyResponse()

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    with pytest.raises(InstagramApiException) as ei:
        await messenger.send_text("hello", "user_1")

    assert ei.value.status_code == 200
    assert ei.value.response_text == "<not-json>"


@pytest.mark.asyncio
async def test_send_text_missing_message_id(monkeypatch):
    messenger = InstagramMessenger(access_token="token")

    class DummyResponse:
        status_code = 200
        def json(self):
            return {"ok": True}
        @property
        def text(self):
            return json.dumps(self.json())

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None):
            return DummyResponse()

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    with pytest.raises(InstagramApiException) as ei:
        await messenger.send_text("hello", "user_1")

    assert ei.value.status_code == 200
    assert ei.value.response_json == {"ok": True}
