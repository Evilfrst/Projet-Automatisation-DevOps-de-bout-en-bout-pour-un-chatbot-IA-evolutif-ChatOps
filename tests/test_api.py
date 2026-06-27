from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import backend.app.main as main


client = TestClient(main.app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("backend.app.main.openai_client.chat.completions.create")
@patch("backend.app.main.SessionLocal")
def test_chat(mock_db, mock_create):

    def fake_current_user():
        return SimpleNamespace(
            id=1,
            username="test_user",
            role="admin"
        )

    main.app.dependency_overrides[
        main.get_current_user
    ] = fake_current_user

    mock_session = mock_db.return_value

    mock_create.return_value.choices = [
        SimpleNamespace(
            message=SimpleNamespace(
                content="Bonjour depuis le mock",
                tool_calls=None
            )
        )
    ]

    try:
        response = client.post(
            "/api/chat",
            json={"prompt": "hello"}
        )

        assert response.status_code == 200
        assert response.json()["response"] == "Bonjour depuis le mock"

    finally:
        main.app.dependency_overrides.clear()
