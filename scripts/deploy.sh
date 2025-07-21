#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

echo "Pulling latest changes from GitHub..."
git pull origin main

CONTAINER_ID=$(docker ps -q --filter "publish=8080")
if [ -n "$CONTAINER_ID" ]; then
    echo "Found a container ($CONTAINER_ID) using port 8080. Stopping and removing it..."
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
fi

echo "Building Docker image..."
docker build -t conlit-app .

echo "Starting new container..."
docker run -d --name conlit-container --env-file .env -p 8080:8080 conlit-app

echo "Deployment successful!"
