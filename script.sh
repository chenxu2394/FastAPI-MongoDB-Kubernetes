#!/bin/bash

# Set error handling
set -e

# Define constants
FASTAPI_IMAGE="fast-api-backend:v1"
MONGO_IMAGE="mongo:6.0.6"

# Step 1: Start a new Kubernetes cluster using Kind
echo "Creating a Kubernetes cluster with Kind..."
kind create cluster

# Step 2: Build the FastAPI Docker image
echo "Building the FastAPI Docker image..."
docker build -t fast-api-backend:v1 -f ./backend/Dockerfile ./backend/

# Step 3: Load the Docker image into Kind
echo "Loading the FastAPI Docker image into the Kind cluster..."
kind load docker-image $FASTAPI_IMAGE

# Check if MongoDB image is present locally, if not pull it
if [[ "$(docker images -q $MONGO_IMAGE 2> /dev/null)" == "" ]]; then
  echo "Pulling MongoDB Docker image..."
  docker pull $MONGO_IMAGE
fi

# Load MongoDB image into Kind
echo "Loading the MongoDB Docker image into the Kind cluster..."
kind load docker-image $MONGO_IMAGE

# Step 4: Apply the Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f ./manifests/persistent-volume.yaml
kubectl apply -f ./manifests/mongo.yaml
kubectl apply -f ./manifests/fastapi.yaml

# Step 5: Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --all --timeout=300s

# Step 6: Expose port for testing
kubectl port-forward service/fast-api-service 5000:5000

# Step 7: Cleanup
echo "Cleanup..."
kind delete cluster
docker rmi $FASTAPI_IMAGE $MONGO_IMAGE

echo "All done."
