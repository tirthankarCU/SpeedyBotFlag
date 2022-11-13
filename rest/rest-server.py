from flask import Flask, request, Response
import jsonpickle
from PIL import Image
import base64
import io
import os
import redis
import hashlib
from minio import Minio

# Initialize the Flask application
app = Flask(__name__)
redisHost = os.getenv("REDIS_HOST") or "redis-svc"
redisPort = os.getenv("REDIS_PORT") or 6000

minioHost = os.getenv("MINIO_HOST") or "minio-svc"
minioUser = os.getenv("MINIO_USER") or "root"
minioPasswd = os.getenv("MINIO_PASSWD") or "root123"
client = Minio(minioHost,secure=False,access_key=minioUser,secret_key=minioPasswd)

@app.route('/apiv1/separate', methods=['POST'])
def rawMusic():
    r=request
    json=jsonpickle.decode(r.data)
    b64_img=json['image']
    img=base64.b64decode(b64_img)
    hash='abc123re2'
    return hash
    
@app.route('/apiv1/add/<int:a>/<int:b>', methods=['GET','POST'])
def add(a,b):
    msg=str(a)+" "+str(b)
    hash=hashlib.sha256(msg.encode('utf-8')).hexdigest()
    
    rKV=redis.Redis(host=redisHost,port=redisPort)
    rKV.rpush('msgQ',hash)
    
    client.fput_object('my-bucket',hash,msg)

    response = {'hash' : str(hash)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=5000)