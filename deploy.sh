#!/bin/bash

set -e

cd ~/uptimehub

echo "Pulling latest image..."
docker compose pull

echo "Starting updated container..."
docker compose up -d

echo "Checking service..."
sleep 5

curl -f http://127.0.0.1:5000/health

echo "Deployment successful."
