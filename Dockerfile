
FROM arm32v7/python:3.7-buster
COPY ./qemu-arm-static /usr/bin/qemu-arm-static

ARG PROJ_DIR=/opt/selfie-robot
WORKDIR $PROJ_DIR

RUN echo "\
deb http://deb.debian.org/debian jessie main" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
libatlas3-base libwebp6 libtiff5 libjasper1 libilmbase23 libopenexr23 libavcodec58 libavformat58 libavutil56 \
libswscale5 libgtk-3-0 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 libcairo-gobject2 libcairo2 libgdk-pixbuf2.0-0 \
openjdk-11-jre-headless

ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r ./requirements.txt

ENV LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
RUN python3 -c "import cv2"

COPY ./imgproc ./imgproc
COPY ./robot-pics ./robot-pics

COPY ./utils ./utils

COPY ./build ./build
COPY ./start_app.sh ./start_app.sh

ENTRYPOINT "/bin/bash"
