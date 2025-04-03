
if exist "%~dp0app/whisper_models" (

	docker run -e PYTHONUNBUFFERED=1 -v "%~dp0_output":/code/app/res/processed speech_bubbler

) else (

	docker run -e PYTHONUNBUFFERED=1 -v "%~dp0_output":/code/app/res/processed -v "%~dp0app/whisper_models":/code/app/whisper_models speech_bubbler

)