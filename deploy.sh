#!/bin/bash

set -e

cd ~/uptimehub

echo "Pulling latest image..."
docker compose pull

echo "Starting updated container..."
docker compose up -d

echo "Waiting for container to become healthy..."

for i in {1..12}; do
    STATUS=$(docker compose ps --format '{{.Health}}')

    if [ "$STATUS" = "healthy" ]; then
        echo "Container is healthy."
        echo "Deployment successful."
        exit 0
    fi

    echo "Health status: $STATUS"
    sleep 5
done

echo "Deployment failed: container did not become healthy."
exit 1
