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
rKV=redis.Redis(host=redisHost,port=redisPort,db=0)
rlogs=redis.Redis(host=redisHost,port=redisPort,db=1)

minioHost = os.getenv("MINIO_HOST") or "minio-svc:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
client = Minio(minioHost,secure=False,access_key=minioUser,secret_key=minioPasswd)
bucket_name_ip='queue'
bucket_name_op='result'

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
    rlogs.rpush('logging',f'REST: 1. Pushed Msg {msg}')
    hash=hashlib.sha256(msg.encode('utf-8')).hexdigest()
    rlogs.rpush('logging',f'REST: 2. Hashed Hash {hash}')
    
    file=open(f"{hash}.dat",'w')
    rKV.rpush('MSGQ',hash)
    file.write(msg)
    file.close()
    if not client.bucket_exists(bucket_name_ip):
        print(f"Create bucket {bucket_name_ip}")
        client.make_bucket(bucket_name_ip)
    client.fput_object(bucket_name_ip,f"{hash}.dat",f"./{hash}.dat")

    response = {'hash' : str(hash)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/fetch/<hash>', methods=['GET','POST'])
def fetch(hash):
    rlogs.rpush('logging',f'REST-F: 1. Hash Rx {hash}')
    file=client.get_object(bucket_name_op,f'sum.o',f'./{hash}/sum.o')
    rlogs.rpush('logging',f'REST-F: 2. Get Res from Min.io')
    for data in file:
        res=data.decode('utf-8')
    rlogs.rpush('logging',f'REST-F: 3. Fetched result {res}')
    response = {'result' : str(res)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=5000)