# Speech Bubbler
A python app that takes input video file(s) and generates a modified version with speech bubbles originating from any speaker.


## Usage
- Install using one of the methods listed under **Installing**
- Place desired .mp4 file(s) in ```/app/res/video/```
- Run the app according to how you installed it
- Output is placed in ```/_output/``` (in the root folder)

---

## Installing
### Docker (recommended)
- Install [Docker Desktop](https://www.docker.com/)
- Download and extract this repository
- First time use requires running ```BUILD.bat```
  - This can take upwards of 30 minutes on low end machines because OpenAI-Whisper is absolutely massive

#### After built, ```RUN.bat``` can be used to initiate the app
---
### Manual
- Install:
  - [Python 3.12.4](https://www.python.org/)
  - [FFmpeg](https://www.ffmpeg.org/)
  - [CMake](https://cmake.org/)

Ensure Python and FFmpeg are added to your PATH (you must restart any CMD)

- Download and extract this repository
- Navigate a CMD to the root of the extracted app (where ```RUN.bat``` and ```BUILD.bat``` are)
- Enter the commands:
```
- python -m venv .venv
- .venv\scripts\activate
- python -m pip install --upgrade pip
- pip install -r ./requirements.txt
```
#### The command ```python ./app/main.py``` initiates the app
- You must always run ```.venv\scripts\activate``` before initating the app when using a fresh CMD
  - The virtual enviornment being initiated is denoted by ```(.venv)``` being present before the current path in the console
    
---

#### Dependencies
- Python
  - openai-whisper (20240930)
    - whisper model ```small.en```
  - face-recognition (1.3.0)
  - moviepy (2.1.2)
  - opencv-python (4.11.0.86)
- FFmpeg
- Cmake
