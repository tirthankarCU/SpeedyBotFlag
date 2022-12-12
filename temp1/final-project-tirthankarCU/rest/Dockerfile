FROM python:3.8

RUN  mkdir -p app \
    git clone https://github.com/pallets/flask && \
    pip install flask \
    pip install jsonpickle \
    pip install pillow \
    pip install minio \
    pip install flask flask-wtf redis Flask-Debug

COPY rest-server.py /app

ENV	FLASK_PORT 5000

CMD	[ "/bin/sh", "-c", "python /app/rest-server.py" ]
