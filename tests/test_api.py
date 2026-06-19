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
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("backend.app.main.client.chat.completions.create")
def test_chat(mock_create):

    def fake_current_user():
        return SimpleNamespace(
            id=1,
            username="test_user",
            role="admin"
        )

    main.app.dependency_overrides[
        main.get_current_user
    ] = fake_current_user

    mock_create.return_value.choices = [
        type(
            "obj",
            (object,),
            {
                "message": type(
                    "obj",
                    (object,),
                    {
                        "content": "Bonjour depuis le mock"
                    }
                )()
            }
        )()
    ]

    try:
        response = client.post(
            "/chat",
            json={"prompt": "hello"}
        )

        assert response.status_code == 200
        assert response.json()["response"] == "Bonjour depuis le mock"

    finally:
        main.app.dependency_overrides.clear()
