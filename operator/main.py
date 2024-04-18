from flask import Flask, request, jsonify
from kubernetes import client, config

app = Flask(__name__)

# Load Kubernetes configuration from default location
config.load_incluster_config()

@app.route('/training', methods=['POST'])
def create_training_job():
    # Create an instance of the Kubernetes BatchV1Api client
    batch_v1_api = client.BatchV1Api()

    # Define the Job resource with the correct restart policy
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="hello-world-job"),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    restart_policy="Never",  # or "OnFailure"
                    containers=[
                        client.V1Container(
                            name="ubuntu",
                            image="ubuntu",
                            command=["echo", "hello world"]
                        )
                    ]
                )
            ),
            # Ensure that the Job does not automatically restart
            backoff_limit=0
        )
    )

    try:
        # Create the Job in the cluster
        batch_v1_api.create_namespaced_job(namespace="default", body=job)
        return jsonify({'message': 'Training job created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
