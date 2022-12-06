
FROM python:3.8

RUN  mkdir -p app \
    git clone https://github.com/pallets/flask && \
    pip install flask \
    pip install minio \
    pip install pytorch-lightning==1.5.1 \
    pip install torch==1.10.0 \
    pip install transformers==4.17.0 \
    pip install kaggle==1.5.8 \
    pip install pandas==1.1.2 \
    pip install scikit-learn==0.23.2 \
    pip install datasets==1.0.2 \
    pip install tqdm==4.41.0 \
    pip install sentencepiece==0.1.94 \
    pip install detoxify \
    pip install flask flask-wtf redis Flask-Debug 

COPY worker-server.py /app

ENV	FLASK_PORT 5000

CMD	[ "/bin/sh", "-c", "python /app/worker-server.py" ]