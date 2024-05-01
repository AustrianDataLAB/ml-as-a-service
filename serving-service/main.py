from flask import Flask, request, send_file, jsonify
import requests

app = Flask(__name__)
model = None

PERSISTENCE_SERVICE_URL = "http://persistence-service:5000"

#---------------------------------------------------------------------
#-----------------------------functions-------------------------------
#---------------------------------------------------------------------


def load_model():
    try:
        response = requests.get(PERSISTENCE_SERVICE_URL)
        if response.status_code == 200:
            #TODO set model
            return 'Success', 200
        else:
            return 'Failure', 500
    except Exception as e:
        return jsonify({'Error': f"Error: {str(e)}"}), 505
    
def inference(data):
    #TODO actual inference    
    return "Image is 100% cat!", 200



#---------------------------------------------------------------------
#---------------------------------API---------------------------------
#---------------------------------------------------------------------

@app.route('/infer', methods=['POST'])
def get_model():
    return inference(request)

    
@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World!"


if __name__ == '__main__':
    # load_model()
    app.run(host='0.0.0.0', port=5001)
