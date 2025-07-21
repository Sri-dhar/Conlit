#!/bin/bash

set -e
git pull origin main
docker build -t conlit-app .

if [ "$(docker ps -q -f name=conlit-container)" ]; then
    docker stop conlit-container
    docker rm conlit-container
fi

docker run -d --name conlit-container --env-file .env -p 8080:8080 conlit-app
