import pytest
import os

from ..main import create_app, load_env, upload_data


AUTH_TOKEN = "12341234-aklasiueon"
TEST_FILE_PATH = "data/corki.webp"
TEST_FILE_CONTENT = "This is a test file."


import os
from dotenv import load_dotenv


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_azurite_contaienr():
    load_env()
    upload_data("test","test_file.txt","This is a test file.","text/plain")

#-------------------Test cases for the hello world endpoint-------------------


def test_should_status_code_ok(client):
	response = client.get('/')
	assert response.status_code == 200

def test_should_return_hello_world(client):
	response = client.get('/')
	data = response.data.decode() #Decodes the request data
	assert data == 'Hello, World!'
     
	 
#-------------------Test cases for the data endpoints -------------------

def test_POST_data_with_token(client):
    # Define the file path to be uploaded
    file_path = 'data/test_file.txt'

    # Create a test file
    with open(file_path, 'w') as f:
        f.write(TEST_FILE_CONTENT)

    # Send a POST request with the file
    with open(file_path, 'rb') as f:
        response = client.post('/data', headers={'Authorization': AUTH_TOKEN}, data={'file': (f, 'test_file.txt')})

    # Assert the response
    assert response.status_code == 200
    assert str(response.data).__contains__("successfully")

    # Clean up the test file
    os.remove(file_path)


def test_GET_data_with_valid_token(client):
    # Send a GET request with a valid token
    response = client.get('/data', headers={'Authorization': AUTH_TOKEN})
    print(response.text)
    assert response.status_code == 200
    assert response.text == TEST_FILE_CONTENT


def test_GET_data_without_token(client):
    # Send a GET request without the Authorization header
    response = client.get('/data')
    assert response.status_code == 401
    assert response.json == {"error": "Authorization header is missing"}
    

def test_GET_data_with_malformed_token(client):
    # Send a GET request with an invalid Authorization header format
    response = client.get('/data', headers={'Authorization': 'invalid_format'})
    assert response.status_code == 401
    assert response.json == {"error": "Invalid Authorization header format"}


#-------------------Test cases for the model endpoints -------------------

def test_POST_model_with_token(client):
    # Define the file path to be uploaded
    file_path = 'data/test_file.txt'

    # Create a test file
    with open(file_path, 'w') as f:
        f.write(TEST_FILE_CONTENT)

    # Send a POST request with the file
    with open(file_path, 'rb') as f:
        response = client.post('/model', headers={'Authorization': AUTH_TOKEN}, data={'file': (f, 'test_file.txt')})

    # Assert the response
    assert response.status_code == 200
    assert str(response.data).__contains__("successfully")

    # Clean up the test file
    os.remove(file_path)


def test_GET_model_with_valid_token(client):
    # Send a GET request with a valid token
    response = client.get('/model', headers={'Authorization': AUTH_TOKEN})
    print(response.text)
    assert response.status_code == 200
    assert response.text == TEST_FILE_CONTENT


def test_GET_model_without_token(client):
    # Send a GET request without the Authorization header
    response = client.get('/model')
    assert response.status_code == 401
    assert response.json == {"error": "Authorization header is missing"}
    

def test_GET_model_with_malformed_token(client):
    # Send a GET request with an invalid Authorization header format
    response = client.get('/model', headers={'Authorization': 'invalid_format'})
    assert response.status_code == 401
    assert response.json == {"error": "Invalid Authorization header format"}