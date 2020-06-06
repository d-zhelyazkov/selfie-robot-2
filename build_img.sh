#!/bin/bash

# stop on error
set -e

source ./docker.properties

echo "Building image..."
docker build --tag "$IMG_NAME" .

if ping -c 1 "$REGISTRY"; then
  echo "Publishing image..."
  # publish image
  docker tag "$IMG_NAME" "$PUB_PATH"
  docker push "$PUB_PATH"
else
  echo "Registry not available. Image not published."
fi
