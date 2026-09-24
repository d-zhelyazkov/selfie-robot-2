# selfie-robot-2

A two-wheeled robot that finds itself in a camera image and drives to the center of the frame. Built as my MSc thesis project in Artificial Intelligence (Sofia University), 2019–2022.

## How it works

1. **Capture.** An Android phone serves as the camera through a REST API ([android-camera-service](https://github.com/d-zhelyazkov/android-camera-service)); exposure, ISO and focus are set from code.
2. **Detect.** The robot carries two blue LEDs on its sides and a red one on its tail. Each frame is converted to HSV, and each color channel is thresholded with Otsu's method to extract the LED points (`imgproc/`).
3. **Localize.** The three points give the robot's position and heading in image coordinates (`src/robot_finder.py`, `src/geometry.py`).
4. **Move.** The offset from the frame center is turned into turn and drive commands, sent over serial to an Arduino motor controller ([arduino-2WD-controller](https://github.com/d-zhelyazkov/arduino-2WD-controller)) that uses wheel encoders for precise motion.

The loop is reactive (RxPY): capture, processing and motion run as event streams on separate threads. It runs on a Raspberry Pi and is built as an ARM Docker image (`Dockerfile`, `build_img.sh`).

`imgproc/eval.py` measures the detection success rate over a folder of recorded images; `analyze.ipynb` studies detection outliers from the recorded LED geometry.

## Stack

Python · OpenCV · NumPy · RxPY · Raspberry Pi · Arduino · Docker

The first version, an Android app talking to the robot over Bluetooth, is [selfie-robot](https://github.com/d-zhelyazkov/selfie-robot).
