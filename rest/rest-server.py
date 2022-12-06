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
rKV=redis.Redis(host=redisHost,port=redisPort,db=0) # insert user-tweet & bad tweets
rlogs=redis.Redis(host=redisHost,port=redisPort,db=1) # insert logs 

minioHost = os.getenv("MINIO_HOST") or "minio-svc:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
client = Minio(minioHost,secure=False,access_key=minioUser,secret_key=minioPasswd)
bucket_name_ip1='legit'
bucket_name_ip2='tobechecked'
bagOfWords={'motherfucker':1,'rape':1,'kill':1,'fuck':1,'kill you':1,'rape you':1}

@app.route('/apiv1/post', methods=['GET'])
def post():
    r=request
    json_=jsonpickle.decode(r.data)
    rlogs.rpush('logging','REST: 1. Msg Rx')
    prev=''
    cnt=0
    text=json_['text']
    user=json_['user']
    for word in text.split():
        two_words=prev+' '+word.lower()
        if word.lower() in bagOfWords or two_words in bagOfWords:
            cnt+=1
        prev=word.lower()
    msg='ACK'
    if cnt>=1:
        msg='NACK'
    response = {'hash' : msg,'reason':'User post processed(initial).'}
    response_pickled = jsonpickle.encode(response)
    hash=hashlib.sha256(text.encode('utf-8')).hexdigest()
    file=open(f"{hash}.{user}",'w')
    file.write(text)
    file.close()
    if msg=='NACK':
        if not client.bucket_exists(bucket_name_ip2):
            print(f"Create bucket {bucket_name_ip2}")
            client.make_bucket(bucket_name_ip2)
        client.fput_object(bucket_name_ip2,f"{hash}.{user}",f"./{hash}.{user}")
        rlogs.rpush('logging',f'REST: 2. Minio stored.(NACK)')
        rKV.rpush('bad',f"{hash}.{user}")
        rlogs.rpush('logging',f'REST: 3. Bad tweet pushed')
    else:
        if not client.bucket_exists(bucket_name_ip1):
            print(f"Create bucket {bucket_name_ip1}")
            client.make_bucket(bucket_name_ip1)
        client.fput_object(bucket_name_ip1,f"{hash}.{user}",f"./{hash}.{user}")
        rlogs.rpush('logging',f'REST: 2. Minio stored.(ACK)')
        if rKV.exists(user)==True:
            value=rKV.get(user).decode('utf-8')
            value=value+';'+f"{hash}.{user}"
            rKV.set(user,value)
        else:
            rKV.set(user,f"{hash}.{user}")
        log_var=rKV.get(user).decode('utf-8')
        rlogs.rpush('logging',f'REST: 3. KV store {log_var}')
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/fetch',methods=['GET'])
def fetch():
    r=request
    json_=jsonpickle.decode(r.data)    
    user=json_['user']
    if rKV.exists(user)==True:
        posts=rKV.get(user).decode('utf-8')
        sen=""
        for tweetId in posts.split(';'):
            client.get_object(bucket_name_ip1,f'{tweetId}',f'{bucket_name_ip1}/{tweetId}')
            rlogs.rpush('logging',f'REST: 1. Min.io(fetch)')
            file=open(f"{tweetId}",'r')
            for data in file:
                sen=sen+data
            sen=sen+"[SEP]"
        print(sen)
        response = {'data' : sen,'reason':'Valid User Posts.'}
        response_pickled = jsonpickle.encode(response)
    else:
        response = {'data' : 'X','reason':'User Doesn\'t Exist.'}
        response_pickled = jsonpickle.encode(response)       
    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=5000)