@echo off

if not exist "%~dp0app/whisper_models/small.en.pt" (
	
	echo "whisper model 'small.en.pt' not found - downloading'
	powershell -Command "Invoke-WebRequest https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt -OutFile %~dp0app/whisper_models/small.en.pt"

)

docker build -t speech_bubbler .