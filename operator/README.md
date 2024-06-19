# Flask Kubernetes Application

This application provides a Flask-based API to manage Kubernetes resources, specifically for training jobs and serving deployments. It utilizes the Kubernetes Python client to interact with a Kubernetes cluster, handling tasks like creating, monitoring, and deleting jobs and deployments.

## Prerequisites

Ensure you have the following environment variables set before running the application:

- `TRAINING_IMAGE`
- `SERVING_IMAGE`
- `NAMESPACE`
- `SERVING_PORT`
- `PERSISTENCE_SERVICE_URI`
- `DOMAIN`

These environment variables are essential for the application to interact with Kubernetes and handle the deployment configurations.

## API Endpoints

### Create a Training Job
**Endpoint:** `/training`  
**Method:** `POST`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Creates a new training job if no job is currently running for the tenant. If a job is already running, it returns an error.

**Response:**
- `202 Accepted`: Training job created.
- `400 Bad Request`: Training job is already running.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

### Get Status of All Training Jobs
**Endpoint:** `/training`  
**Method:** `GET`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Retrieves the status of all training jobs for the tenant.

**Response:**
- `200 OK`: List of jobs and their statuses.
- `404 Not Found`: No jobs found for the tenant.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

### Get Status of a Specific Training Job
**Endpoint:** `/training/<id>`  
**Method:** `GET`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Retrieves the status of a specific training job by its ID.

**Response:**
- `200 OK`: Status of the job.
- `404 Not Found`: Job not found.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

### Create a Serving Deployment
**Endpoint:** `/serving`  
**Method:** `POST`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Creates a new serving deployment for the tenant. If a deployment already exists, it returns an error.

**Response:**
- `201 Created`: Serving deployment created.
- `400 Bad Request`: Serving deployment already exists.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

### Get Status of Serving Deployment
**Endpoint:** `/serving`  
**Method:** `GET`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Retrieves the status of the serving deployment for the tenant.

**Response:**
- `200 OK`: Status of the deployment.
- `404 Not Found`: Deployment not found.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

### Delete Serving Deployment
**Endpoint:** `/serving`  
**Method:** `DELETE`  
**Headers:**  
- `Authorization`: Tenant identifier

**Description:** Deletes the serving deployment for the tenant.

**Response:**
- `200 OK`: Deployment deleted.
- `404 Not Found`: Deployment not found.
- `500 Internal Server Error`: An error occurred with the Kubernetes API.

## Installation

Apply the manifest.yaml file to your kubernetes cluster.