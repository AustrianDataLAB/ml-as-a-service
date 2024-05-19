from flask import Flask, request, jsonify
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import os
import sys
import logging
import uuid

# Define the required environment variables
REQUIRED_ENV_VARS = [
    "TRAINING_IMAGE",
    "SERVING_IMAGE",
    "NAMESPACE",
    "SERVING_PORT",
    "PERSISTENCE_SERVICE_URI",
    "DOMAIN",
]

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

# Create an insteance of the Kubernetes ExtensionsV1beta1Api client
networking_v1_api = client.NetworkingV1Api()

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

    # Define the ConfigMap resource with the required environment variables
    config_map = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(
            name="training-" + auth_header + "-" + random_uuid,
            labels={"app": "training", "tenant": auth_header, "id": random_uuid},
        ),
        data={
            "PERSISTENCE_SERVICE_URI": os.getenv("PERSISTENCE_SERVICE_URI"),
            "UUID": random_uuid,
            "TENANT": auth_header,
        },
    )

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
                            env=[
                                client.V1EnvVar(
                                    name="PERSISTENCE_SERVICE_URI",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="training-"
                                            + auth_header
                                            + "-"
                                            + random_uuid,
                                            key="PERSISTENCE_SERVICE_URI",
                                        )
                                    ),
                                ),
                                client.V1EnvVar(
                                    name="TENANT",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="training-"
                                            + auth_header
                                            + "-"
                                            + random_uuid,
                                            key="TENANT",
                                        )
                                    ),
                                ),
                                client.V1EnvVar(
                                    name="UUID",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="training-"
                                            + auth_header
                                            + "-"
                                            + random_uuid,
                                            key="UUID",
                                        )
                                    ),
                                ),
                            ],
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
        # Create the ConfigMap in the cluster
        core_v1_api.create_namespaced_config_map(namespace=auth_header, body=config_map)
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

    # Define the ConfigMap resource with the required environment variables
    config_map = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(
            name="serving-" + auth_header,
            labels={"app": "serving", "tenant": auth_header},
        ),
        data={
            "PERSISTENCE_SERVICE_URI": os.getenv("PERSISTENCE_SERVICE_URI"),
            "TENANT": auth_header,
        },
    )

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
                match_labels={"app": "serving", "tenant": auth_header}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "serving", "tenant": auth_header}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="serving-" + auth_header,
                            image=os.getenv("SERVING_IMAGE"),
                            ports=[
                                client.V1ContainerPort(
                                    container_port=int(os.getenv("SERVING_PORT"))
                                )
                            ],
                            env=[
                                client.V1EnvVar(
                                    name="PERSISTENCE_SERVICE_URI",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="serving-" + auth_header,
                                            key="PERSISTENCE_SERVICE_URI",
                                        )
                                    ),
                                ),
                                client.V1EnvVar(
                                    name="TENANT",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="serving-" + auth_header, key="TENANT"
                                        )
                                    ),
                                ),
                            ],
                        )
                    ]
                ),
            ),
        ),
    )

    # Define the Service resource with NodePort type
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name="serving-" + auth_header,
            labels={"app": "serving", "tenant": auth_header},
        ),
        spec=client.V1ServiceSpec(
            selector={"app": "serving", "tenant": auth_header},
            ports=[client.V1ServicePort(port=int(os.getenv("SERVING_PORT")))],
            type="NodePort",
        ),
    )

    # Define the Ingress resource
    ingress = client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(
            name="serving-" + auth_header,
            labels={"app": "serving", "tenant": auth_header},
        ),
        spec=client.V1IngressSpec(
            rules=[
                client.V1IngressRule(
                    host=os.getenv("DOMAIN"),
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path="/serving/" + auth_header,
                                path_type="Prefix",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name="serving-" + auth_header,
                                        port=client.V1ServiceBackendPort(
                                            number=int(os.getenv("SERVING_PORT"))
                                        ),
                                    )
                                ),
                            )
                        ]
                    ),
                )
            ]
        ),
    )

    try:
        # Create the ConfigMap in the cluster
        core_v1_api.create_namespaced_config_map(namespace=auth_header, body=config_map)
        logging.info(f"Serving ConfigMap created successfully for {auth_header}")

        # Create the Deployment in the cluster
        apps_v1_api.create_namespaced_deployment(namespace=auth_header, body=deployment)
        logging.info(f"Serving deployment created successfully for {auth_header}")

        # Create the Service in the cluster
        core_v1_api.create_namespaced_service(namespace=auth_header, body=service)
        logging.info(f"Serving service created successfully for {auth_header}")

        # Create the Ingress in the cluster
        networking_v1_api.create_namespaced_ingress(namespace=auth_header, body=ingress)
        logging.info(f"Serving ingress created successfully for {auth_header}")

        return (
            jsonify(
                {"url": "https://" + os.getenv("DOMAIN") + "/serving/" + auth_header}
            ),
            201,
        )
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

        # Fetch the Service from the cluster
        service = core_v1_api.read_namespaced_service(
            name="serving-" + auth_header, namespace=auth_header
        )

        # Fetch the Ingress from the cluster
        ingress = networking_v1_api.read_namespaced_ingress(
            name="serving-" + auth_header, namespace=auth_header
        )

        logging.info(
            f"Serving deployment status for {auth_header}: {deployment.status}"
        )
        return (
            jsonify(
                {"available": True if deployment.status.available_replicas else False,
                 "url": "https://" + os.getenv("DOMAIN") + "/serving/" + auth_header}
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
        # Delete the Service from the cluster
        core_v1_api.delete_namespaced_service(
            name="serving-" + auth_header, namespace=auth_header
        )
        logging.info(f"Serving service deleted successfully for {auth_header}")
        # Delete the Ingress from the cluster
        networking_v1_api.delete_namespaced_ingress(
            name="serving-" + auth_header, namespace=auth_header
        )
        logging.info(f"Serving ingress deleted successfully for {auth_header}")
        # Delete the ConfigMap from the cluster
        core_v1_api.delete_namespaced_config_map(
            name="serving-" + auth_header, namespace=auth_header
        )


        return jsonify(), 200
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
