from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("backend.app.main.client.chat.completions.create")
def test_chat(mock_create):

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

    response = client.post(
        "/chat",
        json={"prompt": "hello"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert data["response"] == "Bonjour depuis le mock"
