#!/bin/bash

# stop on error
set -e
set -x

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

DATA_DIR=${1:-"/mnt/data/robot_imgs/"}
MOTION="${MOTION:-true}"

echo "Running image..."
docker run \
  -it \
  --privileged \
  -e MOTION="$MOTION" \
  --volume "$DATA_DIR:/mnt/data/robot_imgs/" \
  --volume "/dev/:/dev/" \
  --entrypoint "/opt/selfie-robot/src/random_robot.py" \
  "$IMG_NAME"
