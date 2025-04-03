FROM python:3.12.4

RUN apt-get update && apt-get install -y \
    ffmpeg \
    cmake

RUN pip install --upgrade pip

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["python", "app/main.py"]