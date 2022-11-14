
FROM python:3.8

RUN  mkdir -p app \
    git clone https://github.com/pallets/flask && \
    pip install flask \
    pip install demucs \
    pip install minio \
    pip install flask flask-wtf redis Flask-Debug 

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && \
    apt-get install -yq ffmpeg
    
COPY worker-server.py /app
ADD data /app/

ENV	FLASK_PORT 5000

CMD	[ "/bin/sh", "-c", "python /app/worker-server.py" ]