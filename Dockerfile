FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu24.04

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y python3-venv python3-pip

COPY requirements.txt .

RUN python3 -m venv venv
RUN ./venv/bin/pip3 install --no-cache-dir -r requirements.txt

COPY jaa.py ./
COPY main.py ./
COPY log_config.yaml ./
COPY app ./app
COPY plugins ./plugins
COPY static ./static
COPY resources ./resources

EXPOSE 4990

RUN mkdir -p /app/files_processing/in && mkdir -p /app/files_processing/out && mkdir -p /app/models && mkdir -p /app/options

CMD ["./venv/bin/python3", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=4990", "--log-level=info", "--log-config=resources/log_config.yaml"]
