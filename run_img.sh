#!/bin/bash

# stop on error
set -e

SELF_NAME=$0
SELF_DIR=$(dirname "$SELF_NAME")

# shellcheck source=./docker.properties
source "$SELF_DIR/docker.properties"

if ping -c 1 "$REGISTRY"; then
  # pull image
  echo "Pulling image from registry..."
  docker pull "$PUB_PATH"
  docker tag "$PUB_PATH" "$IMG_NAME"
else
  echo "Registry not available. Will run local image."
fi

export DISPLAY=:0
xhost +local:

echo "Running image..."
docker run \
  -it \
  --privileged \
  -e DISPLAY="$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --volume "/dev/:/dev/" \
  "$IMG_NAME"
