from flask import Flask, request, jsonify
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import os
import sys
import logging
import hashlib
import uuid

# Define the required environment variables
REQUIRED_ENV_VARS = [
    "TRAINING_IMAGE",
    "SERVING_IMAGE",
    "SERVING_PORT",
    "PERSISTENCE_SERVICE_URI",
    "DOMAIN",
    "TLS_SECRET",
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
logging.info("Loading Kubernetes configuration")
config.load_incluster_config()

# Create an instance of the Kubernetes BatchV1Api client
logging.info("Creating Kubernetes API clients - batch")
batch_v1_api = client.BatchV1Api()

# Create an instance of the Kubernetes AppsV1Api client
logging.info("Creating Kubernetes API clients - apps")
apps_v1_api = client.AppsV1Api()

# Create an instance of the Kubernetes CoreV1Api client
logging.info("Creating Kubernetes API clients - core")
core_v1_api = client.CoreV1Api()

# Create an insteance of the Kubernetes ExtensionsV1beta1Api client
logging.info("Creating Kubernetes API clients - networking")
networking_v1_api = client.NetworkingV1Api()

# Create a Flask app
logging.info("Creating Flask app")
app = Flask(__name__)
logging.info("Flask app created successfully")


# Ensure that the namespace exists, if not create it
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


def _sha1(input_string):
    if isinstance(input_string, str):
        input_string = input_string.encode("utf-8")
    sha256_hash = hashlib.sha1(input_string).hexdigest()
    return sha256_hash


@app.route("/", methods=["GET"])
def alive():
    # Implement check logic here
    return jsonify(success=True), 200


# Define a route to create a training job
@app.route("/training", methods=["POST"])
def create_training_job():
    # Fetch authorization-header
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)
    random_uuid = str(uuid.uuid4())[:10]

    # Check if the Job already exists and is in a running state
    try:
        ensure_namespace_exists(auth_header_hash)

        # List all jobs in the namespace
        jobs = batch_v1_api.list_namespaced_job(namespace=auth_header_hash)

        # Filter jobs based on the name
        filtered_jobs = [
            job.metadata.name
            for job in jobs.items
            if job.metadata.name.startswith("training-" + auth_header_hash)
        ]

        for job_name in filtered_jobs:
            job = batch_v1_api.read_namespaced_job(
                name=job_name, namespace=auth_header_hash
            )
            if job.status.active:
                logging.info(
                    f"Training job already exists and is in a running state for {auth_header_hash}"
                )
                return jsonify({"error": "Training job is running"}), 400
            # Delete the Job if it is in a failed state or has completed
            # elif job.status.failed or job.status.succeeded:
            #    batch_v1_api.delete_namespaced_job(name="training-"+auth_header_hash, namespace=auth_header_hash)
            #    logging.info(f"Training job deleted for {auth_header_hash}")
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
            name="training-" + auth_header_hash + "-" + random_uuid,
            labels={
                "app": "training",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
                "id": random_uuid,
            },
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
            name="training-" + auth_header_hash + "-" + random_uuid,
            labels={
                "app": "training",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
                "id": random_uuid,
            },
        ),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    restart_policy="Never",  # or "OnFailure"
                    containers=[
                        client.V1Container(
                            name="training-" + auth_header_hash,
                            image=os.getenv("TRAINING_IMAGE"),
                            image_pull_policy="Always",
                            env=[
                                client.V1EnvVar(
                                    name="PERSISTENCE_SERVICE_URI",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="training-"
                                            + auth_header_hash
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
                                            + auth_header_hash
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
                                            + auth_header_hash
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
        batch_v1_api.create_namespaced_job(namespace=auth_header_hash, body=job)
        # Create the ConfigMap in the cluster
        core_v1_api.create_namespaced_config_map(
            namespace=auth_header_hash, body=config_map
        )
        logging.info(f"Training job created successfully for {auth_header_hash}")
        return jsonify({"id": random_uuid}), 202
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Define a route to get current states of all training jobs
@app.route("/training", methods=["GET"])
def get_training_jobs():
    # Fetch authorization-header
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)

    try:
        # List all jobs in the namespace
        jobs = batch_v1_api.list_namespaced_job(namespace=auth_header_hash)

        # Filter jobs based on the name
        filtered_jobs = [
            job
            for job in jobs.items
            if job.metadata.name.startswith("training-" + auth_header_hash)
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
                job.metadata.name.replace("training-" + auth_header_hash + "-", "")
            ] = status

        logging.info(f"Training job status for {auth_header_hash}: {job_states}")

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
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)

    try:
        # Fetch the Job from the cluster
        job = batch_v1_api.read_namespaced_job(
            name="training-" + auth_header_hash + "-" + id, namespace=auth_header_hash
        )
        logging.info(f"Training job status for {auth_header_hash}: {job.status}")

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
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)

    # Check if the Deployment already exists
    try:
        ensure_namespace_exists(auth_header_hash)
        deployment = apps_v1_api.read_namespaced_deployment(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )
        if deployment:
            logging.info(f"Serving deployment already exists for {auth_header_hash}")
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
            name="serving-" + auth_header_hash,
            labels={
                "app": "serving",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
            },
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
            name="serving-" + auth_header_hash,
            labels={
                "app": "serving",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
            },
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={
                    "app": "serving",
                    "tenant": auth_header,
                    "tenant-hash": auth_header_hash,
                }
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        "app": "serving",
                        "tenant": auth_header,
                        "tenant-hash": auth_header_hash,
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="serving-" + auth_header_hash,
                            image=os.getenv("SERVING_IMAGE"),
                            image_pull_policy="Always",
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
                                            name="serving-" + auth_header_hash,
                                            key="PERSISTENCE_SERVICE_URI",
                                        )
                                    ),
                                ),
                                client.V1EnvVar(
                                    name="TENANT",
                                    value_from=client.V1EnvVarSource(
                                        config_map_key_ref=client.V1ConfigMapKeySelector(
                                            name="serving-" + auth_header_hash,
                                            key="TENANT",
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
            name="serving-" + auth_header_hash,
            labels={
                "app": "serving",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
            },
        ),
        spec=client.V1ServiceSpec(
            selector={
                "app": "serving",
                "tenant": auth_header,
                "tenant-hash": auth_header_hash,
            },
            ports=[
                client.V1ServicePort(
                    port=80, target_port=int(os.getenv("SERVING_PORT"))
                )
            ],
            type="ClusterIP",
        ),
    )

    # Define the Ingress resource
    # ingress = client.V1Ingress(
    #    api_version="networking.k8s.io/v1",
    #    kind="Ingress",
    #    metadata=client.V1ObjectMeta(
    #        name="serving-" + auth_header_hash,
    #        labels={
    #            "app": "serving",
    #            "tenant": auth_header,
    #            "tenant-hash": auth_header_hash,
    #        },
    #        annotations={"nginx.ingress.kubernetes.io/rewrite-target": "/"},
    #    ),
    #    spec=client.V1IngressSpec(
    #        ingress_class_name="nginx-static",
    #        rules=[
    #            client.V1IngressRule(
    #                host=os.getenv("DOMAIN"),
    #                http=client.V1HTTPIngressRuleValue(
    #                    paths=[
    #                        client.V1HTTPIngressPath(
    #                            path="/serving/" + auth_header_hash,
    #                            path_type="Prefix",
    #                            backend=client.V1IngressBackend(
    #                                service=client.V1IngressServiceBackend(
    #                                    name="serving-" + auth_header_hash,
    #                                    port=client.V1ServiceBackendPort(
    #                                        number=80,
    #                                    ),
    #                                ),
    #                            ),
    #                        )
    #                    ]
    #                ),
    #            )
    #        ],
    #        tls=[
    #            client.V1IngressTLS(
    #                hosts=[os.getenv("DOMAIN")],
    #                secretName=os.getenv("TLS_SECRET"),
    #            )
    #        ],
    #    ),
    # )

    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": "serving-{{auth_header_hash}}",
            "labels": {
                "app": "serving",
                "tenant": "{{auth_header}}",
                "tenant-hash": "{{auth_header_hash}}",
            },
            "annotations": {"nginx.ingress.kubernetes.io/rewrite-target": "/"},
        },
        "spec": {
            "ingressClassName": "nginx-static",
            "rules": [
                {
                    "host": "{{DOMAIN}}",
                    "http": {
                        "paths": [
                            {
                                "path": "/serving/{{auth_header_hash}}",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "serving-{{auth_header_hash}}",
                                        "port": {"number": 80},
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
            "tls": [{"hosts": ["{{DOMAIN}}"], "secretName": "{{TLS_SECRET}}"}],
        },
    }

    try:
        # Create the ConfigMap in the cluster
        core_v1_api.create_namespaced_config_map(
            namespace=auth_header_hash, body=config_map
        )
        logging.info(f"Serving ConfigMap created successfully for {auth_header_hash}")

        # Create the Deployment in the cluster
        apps_v1_api.create_namespaced_deployment(
            namespace=auth_header_hash, body=deployment
        )
        logging.info(f"Serving deployment created successfully for {auth_header_hash}")

        # Create the Service in the cluster
        core_v1_api.create_namespaced_service(namespace=auth_header_hash, body=service)
        logging.info(f"Serving service created successfully for {auth_header_hash}")

        # Create the Ingress in the cluster
        networking_v1_api.create_namespaced_ingress(
            namespace=auth_header_hash, body=ingress
        )
        logging.info(f"Serving ingress created successfully for {auth_header_hash}")

        return (
            jsonify(
                {
                    "url": "https://"
                    + os.getenv("DOMAIN")
                    + "/serving/"
                    + auth_header_hash,
                    "id": auth_header_hash,
                }
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
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)

    try:
        # Fetch the Deployment from the cluster
        deployment = apps_v1_api.read_namespaced_deployment(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )

        # Fetch the Service from the cluster
        service = core_v1_api.read_namespaced_service(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )

        # Fetch the Ingress from the cluster
        ingress = networking_v1_api.read_namespaced_ingress(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )

        logging.info(
            f"Serving deployment status for {auth_header_hash}: {deployment.status}"
        )
        return (
            jsonify(
                {
                    "available": (
                        True if deployment.status.available_replicas else False
                    ),
                    "url": "https://"
                    + os.getenv("DOMAIN")
                    + "/serving/"
                    + auth_header_hash,
                }
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
    auth_header = request.headers.get("x-auth-request-user")
    auth_header_hash = _sha1(auth_header)

    try:
        # Delete the Deployment from the cluster
        apps_v1_api.delete_namespaced_deployment(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )
        logging.info(f"Serving deployment deleted successfully for {auth_header_hash}")
        # Delete the Service from the cluster
        core_v1_api.delete_namespaced_service(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )
        logging.info(f"Serving service deleted successfully for {auth_header_hash}")
        # Delete the Ingress from the cluster
        networking_v1_api.delete_namespaced_ingress(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
        )
        logging.info(f"Serving ingress deleted successfully for {auth_header_hash}")
        # Delete the ConfigMap from the cluster
        core_v1_api.delete_namespaced_config_map(
            name="serving-" + auth_header_hash, namespace=auth_header_hash
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
    app.run(host="0.0.0.0", port=4000, debug=True)
