#!/bin/bash

# stop on error
set -e

./gradlew bootJar

./build_img.sh
