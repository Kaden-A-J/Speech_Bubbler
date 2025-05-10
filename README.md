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
- Make sure Docker Desktop is running and the Docker engine is initialized
- Download and extract this repository
- First time use requires running ```BUILD.bat```
  - This can take upwards of 30 minutes on low end machines because OpenAI-Whisper is absolutely massive
  - **NOTE:** For non-windows systems, you must manually download the whisper model ```small.en.pt``` from [here](https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt) and place it in ```/app/whisper_models/``` BEFORE building

#### After built, ```RUN.bat``` can be used to initiate the app
---
### Manual
- Install:
  - [Python 3.12.4](https://www.python.org/)
  - [FFmpeg](https://www.ffmpeg.org/)
  - [CMake](https://cmake.org/)

Ensure Python and FFmpeg are added to your PATH (you must restart any CMD)

- Download and extract this repository
- Download the whisper model ```small.en.pt``` from [here](https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt) and place it in ```/app/whisper_models/```
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
