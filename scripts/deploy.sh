#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Checking for existing 'conlit-container'..."
if [ "$(docker ps -a -q -f name=conlit-container)" ]; then
    echo "Found existing container named 'conlit-container'. Forcibly removing it..."
    docker rm -f conlit-container
fi

echo "Building Docker image..."
docker build -t conlit-app .

echo "Starting new container..."
docker run -d --name conlit-container --env-file .env -p 8080:8080 conlit-app

echo "Deployment successful! The application should be running."
