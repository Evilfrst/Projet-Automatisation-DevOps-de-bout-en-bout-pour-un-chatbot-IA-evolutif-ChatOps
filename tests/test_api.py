from fastapi.testclient import TestClient
from backend.app.main import app
from unittest.mock import patch

client = TestClient(app)


@patch("backend.app.main.client.chat.completions.create")
def test_chat(mock_openai):

    mock_openai.return_value.choices = [
        type(
            "obj",
            (object,),
            {
                "message": type(
                    "obj",
                    (object,),
                    {
                        "content": "Hello test"
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
def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_chat():
    response = client.post("/chat", json={"prompt": "hello"})
    assert response.status_code == 200
