#!/bin/bash

# stop on error
set -e

java \
  -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=8000 \
  -jar ./build/libs/selfie-robot-0.0.1-SNAPSHOT.jar \
