from flask import Flask, request, jsonify
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import os
import sys
import logging
import uuid

# Define the required environment variables
REQUIRED_ENV_VARS = ["TRAINING_IMAGE", "SERVING_IMAGE", "NAMESPACE"]

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

# Check if all required environment variables are set
for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        logging.error(f"Error: Environment variable {var} is not set")
        sys.exit(f"Error: Environment variable {var} is not set")

# Load Kubernetes configuration from default location
config.load_incluster_config()

# Create an instance of the Kubernetes BatchV1Api client
batch_v1_api = client.BatchV1Api()

# Create an instance of the Kubernetes AppsV1Api client
apps_v1_api = client.AppsV1Api()

# Create an instance of the Kubernetes CoreV1Api client
core_v1_api = client.CoreV1Api()

# Create a Flask app
app = Flask(__name__)


#
def ensure_namespace_exists(namespace):
    try:
        core_v1_api.read_namespace(name=namespace)
    except ApiException as e:
        if e.status == 404:
            # Namespace not found, create it
            ns = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
            core_v1_api.create_namespace(body=ns)
        else:
            raise


# Define a route to create a training job
@app.route("/training", methods=["POST"])
def create_training_job():
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")
    random_uuid = str(uuid.uuid4())

    # Check if the Job already exists and is in a running state
    try:
        ensure_namespace_exists(auth_header)

        # List all jobs in the namespace
        jobs = batch_v1_api.list_namespaced_job(namespace=auth_header)

        # Filter jobs based on the name
        filtered_jobs = [
            job.metadata.name
            for job in jobs.items
            if job.metadata.name.startswith("training-" + auth_header)
        ]

        for job_name in filtered_jobs:
            job = batch_v1_api.read_namespaced_job(name=job_name, namespace=auth_header)
            if job.status.active:
                logging.info(
                    f"Training job already exists and is in a running state for {auth_header}"
                )
                return jsonify({"error": "Training job is running"}), 400
            # Delete the Job if it is in a failed state or has completed
            # elif job.status.failed or job.status.succeeded:
            #    batch_v1_api.delete_namespaced_job(name="training-"+auth_header, namespace=auth_header)
            #    logging.info(f"Training job deleted for {auth_header}")
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            pass
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    # Define the Job resource with the correct restart policy
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            name="training-" + auth_header + "-" + random_uuid,
            labels={"app": "training", "tenant": auth_header, "id": random_uuid},
        ),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    restart_policy="Never",  # or "OnFailure"
                    containers=[
                        client.V1Container(
                            name="training-" + auth_header,
                            image=os.getenv("TRAINING_IMAGE"),
                        )
                    ],
                )
            ),
            # Ensure that the Job does not automatically restart
            backoff_limit=0,
        ),
    )

    try:
        # Create the Job in the cluster
        batch_v1_api.create_namespaced_job(namespace=auth_header, body=job)
        logging.info(f"Training job created successfully for {auth_header}")
        return jsonify({"id": random_uuid}), 202
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to get current states of all training jobs
@app.route("/training", methods=["GET"])
def get_training_jobs():
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")

    try:
        # List all jobs in the namespace
        jobs = batch_v1_api.list_namespaced_job(namespace=auth_header)

        # Filter jobs based on the name
        filtered_jobs = [
            job
            for job in jobs.items
            if job.metadata.name.startswith("training-" + auth_header)
        ]

        job_states = {}
        for job in filtered_jobs:
            if job.status.active:
                status = "Active"
            elif job.status.succeeded:
                status = "Succeeded"
            elif job.status.failed:
                status = "Failed"
            else:
                status = "Unknown"
            job_states[
                job.metadata.name.replace("training-" + auth_header + "-", "")
            ] = status

        logging.info(f"Training job status for {auth_header}: {job_states}")

        return jsonify(job_states), 200
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            return jsonify({"error": "Deployment not found"}), 404
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to get current state of a training job
@app.route("/training/<id>", methods=["GET"])
def get_training_job(id):
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")

    try:
        # Fetch the Job from the cluster
        job = batch_v1_api.read_namespaced_job(
            name="training-" + auth_header + "-" + id, namespace=auth_header
        )
        logging.info(f"Training job status for {auth_header}: {job.status}")

        if job.status.active:
            status = "Active"
        elif job.status.succeeded:
            status = "Succeeded"
        elif job.status.failed:
            status = "Failed"
        else:
            status = "Unknown"

        return jsonify({"status": status}), 200
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            return jsonify({"error": "Deployment not found"}), 404
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to create a serving deployment
@app.route("/serving", methods=["POST"])
def create_serving_deployment():
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")

    # Check if the Deployment already exists
    try:
        ensure_namespace_exists(auth_header)
        deployment = apps_v1_api.read_namespaced_deployment(
            name="serving-" + auth_header, namespace=auth_header
        )
        if deployment:
            logging.info(f"Serving deployment already exists for {auth_header}")
            return jsonify({"error": "Serving deployment already exists"}), 400
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            pass
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    # Define the Deployment resource
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name="serving-" + auth_header,
            labels={"app": "serving", "tenant": auth_header},
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": "serving-" + auth_header}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "serving-" + auth_header}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="serving-" + auth_header,
                            image=os.getenv("SERVING_IMAGE"),
                            ports=[client.V1ContainerPort(container_port=8501)],
                            command=["/bin/sh", "-c", "tail -f /dev/null"],
                        )
                    ]
                ),
            ),
        ),
    )

    try:
        # Create the Deployment in the cluster
        apps_v1_api.create_namespaced_deployment(namespace=auth_header, body=deployment)
        logging.info(f"Serving deployment created successfully for {auth_header}")
        return jsonify({"message": "Serving deployment created successfully"}), 201
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to get the status of a serving deployment
@app.route("/serving", methods=["GET"])
def get_serving_deployment():
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")

    try:
        # Fetch the Deployment from the cluster
        deployment = apps_v1_api.read_namespaced_deployment(
            name="serving-" + auth_header, namespace=auth_header
        )
        logging.info(
            f"Serving deployment status for {auth_header}: {deployment.status}"
        )
        return (
            jsonify(
                {"status": "OK" if deployment.status.available_replicas else "FAILING"}
            ),
            200,
        )
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            return jsonify({"error": "Deployment not found"}), 404
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to remove a serving deployment
@app.route("/serving", methods=["DELETE"])
def delete_serving_deployment():
    # Fetch authorization-header
    auth_header = request.headers.get("Authorization")

    try:
        # Delete the Deployment from the cluster
        apps_v1_api.delete_namespaced_deployment(
            name="serving-" + auth_header, namespace=auth_header
        )
        logging.info(f"Serving deployment deleted successfully for {auth_header}")
        return jsonify({"message": "Serving deployment deleted successfully"}), 200
    except ApiException as e:
        logging.error(f"ApiException occurred: {str(e)}")
        if e.status == 404:
            return jsonify({"error": "Deployment not found"}), 404
        else:
            return jsonify({"error": "An error occurred with the Kubernetes API"}), 500
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    app.run(debug=True)
