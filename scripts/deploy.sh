#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."
echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Building Docker image..."
docker build -t conlit-app .

echo "Stopping and removing existing container if it exists..."
if [ "$(docker ps -q -f name=conlit-container)" ]; then
    docker stop conlit-container
    docker rm conlit-container
fi

echo "Starting new container..."
docker run -d --name conlit-container --env-file .env -p 8080:8080 conlit-app

echo "Deployment successful!"
