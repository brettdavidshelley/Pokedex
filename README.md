# 🧠 Pokédex AI (Raspberry Pi Compatible)
Gotta identify 'em all! This project turns your Raspberry Pi 4B (or local machine) into a fully functional **Pokédex**—complete with image recognition and voice output. It can spot Pokémon using your Pi camera (or webcam) and announce their entries using a synthesized voice, just like in the original show.

## Features
- Image Recognition of Generation 1 Pokémon (~150)
- Voice Output (pyttsx3 or espeak)
- Offline Capability
- Live Camera Input
- YOLOv11n/onnx Lightweight Detection Model

## Hardware Requirements
- GPU that can train large datasets (I used an RTX3070)
- If training on windows, use WSL (Windows Subsystem for Linux)
- Audio output device

## Software
- YOLOv11n for training, export model to .onnx file
- OpenCV (image capture/processing)
- pyttsx3 (local voice synthesis)
- pandas (pokedex entries)

## Installation
- pip install -r requirements.txt
- any other libraries/modules

## Helpful Resources
- YOLOv11: https://www.youtube.com/watch?v=IwI-tg8Dyk8

## Training Yolov11 in Linux/WSL
- About 12.2 hours with my configuration
- Inside "training" folder:
- yolo train model=yolo11n.pt data=data.yaml epochs=200 imgsz=640 device=0 name=pokedex_accurate
- yolo export model=runs/detect/pokedex_accurate/weights/best.pt format=onnx

## Running Main Program
- python detection.py (uses webcam)
- python detection.py --source data/images/image.type
- python detection.py --source data/videos/video.type

## Problems Encountered
This project faced several real-world embedded systems challenges, particularly in balancing hardware compatibility with software performance:

1. Camera Compatibility: 
The Arducam IMX708 was not compatible with OpenCV via default cv2.VideoCapture() due to lack of libcamera integration. The workaround was to take periodic photos using a shell command and reload them, leading to higher latency and CPU usage. A potential fix is to use a different camera such as a webcam that communicates through a USB connection.

2. Environment Conflicts: 
Python environments were needed to manage dependencies for OpenCV and YOLO. However, these environments broke GPIO functionality without complex workarounds, limiting the ability to run everything smoothly within a single environment.

3. Voice Engine Degradation on Linux:
pyttsx3, which is a wrapper for OS compatible text-to-speech voice output libraries, while excellent on Windows, produced low-quality and sometimes unintelligible speech on Raspberry Pi. In addition to this, the program naturally is non-blocking when running on Linux and required more changes to the code for the program to run correctly. This difference affected user experience and highlighted the importance of platform-specific testing.

4. Unreliable SSH for Debugging:
While developing remotely over SSH, frequent disconnects (every 5–10 minutes) hampered live debugging. This slowed down iteration time significantly, especially when testing voice and camera functionality.


## Future Improvements
With additional time and resources, several enhancements could significantly improve the system:

1. LCD Display Integration: 
Add a small LCD screen to display Pokémon names, images, or stats. This would allow silent operation and improve accessibility.

2. Button Controls: 
Implement physical buttons for volume control, navigating entries, and triggering a “Trainer Card” mode to display a personalized ID.

3. LED Indicators: 
Use LEDs to visually indicate system states—boot complete, scan in progress, or detection success.

4. Model Expansion: 
Train and support up to Generation 4 Pokémon to increase utility and showcase broader machine learning training capabilities.

5. Improved Camera Pipeline: 
Replace the snapshot workaround with a true video stream integration, potentially through direct libcamera bindings or an OpenCV patch.

6. Voice Customization: 
Explore creating a custom voice model using Bark or similar libraries for a more authentic Pokédex-like voice, especially since offline support remains a priority.
