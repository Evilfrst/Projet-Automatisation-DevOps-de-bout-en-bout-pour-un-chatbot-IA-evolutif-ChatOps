from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import backend.app.main as main


client = TestClient(main.app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat():
    def fake_current_user():
        return SimpleNamespace(
            id=1,
            username="test_user",
            role="admin",
        )

    mocked_message = SimpleNamespace(
        content="Bonjour depuis le mock",
        tool_calls=None,
    )

    mocked_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=mocked_message,
            )
        ]
    )

    mocked_openai_client = MagicMock()

    mocked_openai_client.chat.completions.create.return_value = (
        mocked_response
    )

    def fake_openai_client():
        return mocked_openai_client

    main.app.dependency_overrides[
        main.get_current_user
    ] = fake_current_user

    main.app.dependency_overrides[
        main.get_openai_client
    ] = fake_openai_client

    try:
        response = client.post(
            "/chat",
            json={"prompt": "hello"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "response": "Bonjour depuis le mock"
        }

        mocked_openai_client.chat.completions.create.assert_called_once()

    finally:
        main.app.dependency_overrides.clear()
