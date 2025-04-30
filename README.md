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

## Future Goals
- Expand to generation 4 Pokémon
- Improve voice by training a model (without cloud API)
- Buttons for volume control
- LEDs for status
- Menu buttons

## Problems
- libcamera doesn't work with cv2 without extensive work arounds.

## Project Components and Roles
1. YOLOv11n (Object Detection): 
The YOLOv11n model is responsible for detecting Pokémon within images. It is the lightweight YOLOv11 model intended for small devices such as a Raspberry Pi. It is trained using labeled data and fine-tuned to recognize approximately 150 Pokémon from 9,568 Generation 1 Pokémon pictures. The model is later exported in ONNX format for lightweight, device-friendly inference.

2. OpenCV (Computer Vision Interface): 
OpenCV is used for capturing images via camera and preparing frames for inference. Due to compatibility issues with libcamera, continuous video streaming was replaced with a workaround: taking still photos every 0.5 seconds and loading them into the program. This reduced processing speed but ensured consistent input handling on the Raspberry Pi.

3. pyttsx3 / espeak (Voice Output): 
The text-to-speech engine converts textual Pokémon entries into spoken output. pyttsx3 was preferred for its cross-platform support and offline capability. However, due to pyttsx3 running concurrently on Linux, espeak was used instead to avoid multithreading issues. Voice quality also had significant degradation on Linux as compared to the Windows version.

4. pandas (Pokédex Database): 
Pandas is used to load and manage Pokémon descriptions from a CSV file or database. This makes it easy to map detected Pokémon to their respective entries and expand the dataset in the future.

5. Aux mini speaker:
Used for audio output on the Raspberry Pi.

6. IMX708 libcamera:
Used for video input on the Raspberry Pi.

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

## Comparison to Real-World Embedded Systems
This project mirrors real-world embedded systems in several ways: 

1. Integration of Heterogeneous Components: 
Like real consumer electronics, it incorporates vision, audio, and hardware I/O into a seamless pipeline.

2. Resource Constraints: 
Optimization was necessary to ensure real-time performance on a Raspberry Pi, similar to embedded products that must function with limited CPU and memory.

3. Platform-Specific Challenges: 
The issues with voice quality and camera access parallel the real challenges developers face in ensuring consistent user experience across devices and operating systems.

4. Other Similar Devices: 
There are many programs that can be downloaded on mobile phones for identifying plants or animals. The concept is pretty much identical except that those can hardly be considered embedded systems. The technology is available, but most people don't see the benefit of buying a new device when their phone works fine. Most of the devices do, however, require an internet connection for cloud API's and cloud databases.

5. Where it falls short: 
In commercial systems, custom chips (e.g., TPUs or ASICs) would be used to accelerate performance and lower power usage, while this project remains software-dependent.

6. Where it accels: 
Many commercial systems require an internet connection for cloud API's. No one wants to be stuck in the middle of nowhere trying to identify a pokémon with a weak internet connection or no connection at all! This system runs completely offline. This system also runs in real time and does not require any interaction (such as pushing a button) to inform the user of relevant pokémon information. This is more accurate the Pokédex seen in the anime.

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
