import os
import sys
import hashlib
from flask import Flask, request, send_file, jsonify

import os
import io
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    global connection_string
    connection_string  = os.getenv("CONNECTION_STRING")

# Create a BlobServiceClient

def get_blob_client(user,blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = user
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
        print(f"Container '{container_name}' created.")
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client

def upload_data(user,blob_name,data,content_type):
    blob_client = get_blob_client(user,blob_name)
    if blob_client.exists():
        blob_client.delete_blob()

    content_settings = ContentSettings(content_type=content_type)
    blob_client.upload_blob(data, content_settings=content_settings)

def download_blob(user, blob_name):
    blob_client = get_blob_client(user,blob_name)
    if not blob_client.exists():
        raise Exception(f"Blob '{blob_name}' does not exist.")

    download_stream = blob_client.download_blob()

    blob_data = io.BytesIO()
    blob_data.write(download_stream.read())
    blob_data.seek(0)  # Reset the stream position to the beginning

    # Get the content type of the blob
    content_type = blob_client.get_blob_properties().content_settings.content_type

    return blob_data, content_type


app = Flask(__name__)

# sha256 helper
def _sha1(input_string):
    if isinstance(input_string, str):
        input_string = input_string.encode('utf-8')
    sha256_hash = hashlib.sha1(input_string).hexdigest()
    return sha256_hash

def _get_user_sha(request):
    #TODO: just a dummy- fix when auth is implemented
    token = request.headers.get('Authorization')
    user_id = token.split("-")[0]
    return _sha1(user_id)


#---------------------------------------------------------------------
#-------------generic upload/download functions-----------------------
#---------------------------------------------------------------------

def _upload_to_blob_storage(request,endpoint):
    if 'file' not in request.files:
        print("No file found in request", file=sys.stderr)
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        print("File is empty", file=sys.stderr)
        return jsonify({"error": "File is empty"}), 400
    
    user = _get_user_sha(request)
    
    content_type = file.content_type
    try:
        upload_data(user,endpoint,file, content_type)
        return 'Data uploaded successfully', 200
    except Exception as e:
        print(e, file=sys.stderr)
        #TODO: differnt code here?
        return jsonify({"error": "Data upload failed"}), 500
   
def _download_from_blob_storage(request,endpoint):
    try:
        user = _get_user_sha(request)
        blob_data, content_type = download_blob(user, endpoint)
        #TODO: maybe dynamic filename?
        return send_file(blob_data,download_name="data", as_attachment=True, mimetype=content_type)
    except Exception as e:
        print(e, file=sys.stderr)
        return jsonify({"error": "Data not found"}), 404



#---------------------------------------------------------------------
#---------------------------------API---------------------------------
#---------------------------------------------------------------------

@app.route('/data', methods=['POST'])
def upload_file():
    return _upload_to_blob_storage(request,"data")

@app.route('/data', methods=['GET'])
def get_file():
    return _download_from_blob_storage(request,"data")

@app.route('/model', methods=['POST'])
def upload_model():
    return _upload_to_blob_storage(request,"model")

@app.route('/model', methods=['GET'])
def get_model():
    return _download_from_blob_storage(request,"model")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/healthcheck')
def healthcheck():
    return 200, 'OK'

@app.before_request
def enforce_auth_header():
    #print('AUTH-HEADER:'+str(request.headers.get('Authorization')), file=sys.stderr)
    #omit for hello world - this might be interesting for heatbeat
    if request.path == '/':
        return
    
    if not request.headers.get('Authorization'):
        #optionally redirect here?
        return jsonify({"error": "Authorization header is missing"}), 401
    
    # validate format
    # TODO: might wann do this with regex once the format is clear
    if not "-" in request.headers.get('Authorization') :
        return jsonify({"error": "Invalid Authorization header format"}), 401


def create_app(config):
    load_env()
    app.config.from_object(config)
    return app

if __name__ == '__main__':
    load_env()
    #app.run(debug=True)
    app.run(host='0.0.0.0')