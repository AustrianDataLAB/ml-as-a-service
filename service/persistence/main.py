import os
import sys
import hashlib
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

# sha256 helper
def calculate_sha256(input_string):
    if isinstance(input_string, str):
        input_string = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256(input_string).hexdigest()
    return sha256_hash

def get_userdata_dir():
    return os.path.join(os.getcwd(),"userdata")

def get_userdir(request):
    auth_token = request.headers.get('Authorization') #can asume auth header is set
    user_id = auth_token.split('-')[0]
    user_data = get_userdata_dir()
    user_dir = os.path.join(user_data,str(calculate_sha256(user_id)))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        os.makedirs(os.path.join(user_dir,"data"))
        os.makedirs(os.path.join(user_dir,"models"))

    return os.path.join(user_data,str(calculate_sha256(user_id)))

@app.route('/data', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file found in request", file=sys.stderr)
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        print("File is empty", file=sys.stderr)
        return jsonify({"error": "File is empty"}), 400
    
    user_dir = get_userdir(request)
    
    file.save(os.path.join(user_dir,"data", file.filename))

    return 'File uploaded successfully under: ' + user_dir.split("/")[-1]+ ' with filename: ' + file.filename


@app.route('/data', methods=['GET'])
def get_file():
    user_dirname =  get_userdir(request)
    cwd = os.getcwd()
    if not os.path.exists(os.path.join(cwd,user_dirname)):
        return 'No file uploaded yet'
    if not os.path.exists(os.path.join(cwd,user_dirname,"data")):
        return 'No file uploaded yet'
    
    
    tmp = os.path.join(cwd,user_dirname,"data")
    print('file'+str(tmp), file=sys.stderr)
    file = os.path.join(cwd,user_dirname,"data",os.listdir(tmp)[0])
   
    return send_file(file, as_attachment=True)    


@app.route('/')
def hello_world():
    return 'Hello, World!'


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
    app.config.from_object(config)
    return app

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')