#!/bin/bash

# stop on error
set -e

SELF_NAME=$0
SELF_DIR=$(dirname $SELF_NAME)

source $SELF_DIR/docker.properties

echo "Building image..."
docker build \
  --tag $IMG_NAME \
  $SELF_DIR/$BUILD_CONTEXT

if ping -c 1 $REGISTRY; then
  echo "Publishing image..."
  # publish image
  docker tag $IMG_NAME $PUB_PATH
  docker push $PUB_PATH
else
  echo "Registry not available. Image not published."
fi
