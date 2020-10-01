#!/bin/bash

# stop on error
set -e

THIS_FILE=${BASH_SOURCE[0]}
# name of this file
THIS_PATH=$(realpath "$THIS_FILE")
# full path to this file
PROJECT_DIR=$(dirname "$THIS_PATH")

# shellcheck source=./docker.properties
source "$PROJECT_DIR/docker.properties"

if ping -c 1 "$REGISTRY"; then
  # pull image
  echo "Pulling image from registry..."
  docker pull "$PUB_PATH"
  docker tag "$PUB_PATH" "$IMG_NAME"
else
  echo "Registry not available. Will run local image."
fi

export DISPLAY=:0
xhost +

echo "Running image..."
docker run \
  -it \
  --network host \
  --privileged \
  --device=/dev/ttyACM0 \
  -e DISPLAY="$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --volume "$PROJECT_DIR:/opt/selfie-robot/" \
  --entrypoint="/bin/bash" \
  "$IMG_NAME"
