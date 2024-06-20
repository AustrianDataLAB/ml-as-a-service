import pytest
import requests_mock
import os
from ..main import create_app

TEST_FILE_PATH = os.path.join("data", "dog.jpg")
MOCK_MODEL_PATH = os.path.join("data", "model_package.zip")


@pytest.fixture(scope="module")
def mocked_requests():
    with open(MOCK_MODEL_PATH, "rb") as zip_file:
        zip_file_content = zip_file.read()

    with requests_mock.Mocker() as m:
        # Mock the GET request to return the zip file
        m.get(
            "http://persistence-service.mlaas.svc.cluster.local:5000/model",
            content=zip_file_content,
            headers={"Content-Type": "application/zip"},
            status_code=200,
        )
        yield m


@pytest.fixture(scope="module")
def client(mocked_requests):
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


# -------------------Test cases for the endpoints-------------------


def test_should_status_code_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_should_return_hello_world(client):
    response = client.get("/")
    data = response.data.decode()
    assert data == "Hello, World!"


def test_should_return_inference(client):
    response = client.post("/infer", data={"file": open(TEST_FILE_PATH, "rb")})
    assert response.status_code == 200
    assert (
        "This image most likely belongs to" in response.data.decode()
    ), "Response does not contain the expected string"
