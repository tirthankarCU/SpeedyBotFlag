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
total_songs=0

@app.route('/apiv1/separate', methods=['POST'])
def separate_():
    global total_songs
    r=request
    json=jsonpickle.decode(r.data)
    b64_img=json['mp3']
    song=base64.b64decode(b64_img)
    hash=hashlib.sha256(song).hexdigest()
    rlogs.rpush('logging',f'REST: 1. Hashed song {hash}.')

    file=open(f"{hash}.mp3",'wb')
    file.write(song)
    file.close()
    rlogs.rpush('logging',f'REST: 2. Data written in file.')
    rKV.rpush('msgq',hash)
    total_songs=rKV.rpush('allSongs',hash)
    rlogs.rpush('logging',f'REST: 3. Redis enqueued. Total songs {total_songs}')

    if not client.bucket_exists(bucket_name_ip):
        print(f"Create bucket {bucket_name_ip}")
        client.make_bucket(bucket_name_ip)
    client.fput_object(bucket_name_ip,f"{hash}.mp3",f"./{hash}.mp3")
    rlogs.rpush('logging',f'REST: 4. Minio stored.')

    response = {'hash' : str(hash),'reason':'Song enqueued for separation'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/queue',methods=['GET'])
def queue_():
    global total_songs
    lis=[]
    for i in range(int(total_songs)):
        hash=rKV.lpop('allSongs').decode('utf-8')
        rKV.rpush('allSongs',hash)
        lis.append(hash)
    response = {'queue' : lis}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/track/<song>/<songType>', methods=['GET'])
def track_(song,songType):
    rlogs.rpush('logging',f'REST-F: 1. song-type {songType}')
    try:
        file=client.get_object(bucket_name_op,f'/{song}/{songType}',f'./{song}/{songType}')
    except ResponseError as err:
        print("Error when adding files.")
        print(err)
    rlogs.rpush('logging',f'REST-F: 2. Get Res from Min.io')
    song_f=open(f'{songType}','wb')
    for data in file:
        song_f.write(data)
    song_f.close()
    rlogs.rpush('logging',f'REST-F: 3. Fetched result')
    response = {f"{songType}":base64.b64encode(open(f'{songType}',"rb").read()).decode('utf-8')}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/remove/<song>/<songType>', methods=['GET'])
def remove_(song,songType):
    global total_songs
    count=0
    flag=False
    for thing in client.list_objects(bucket_name_op, recursive=True):
        obj=thing.object_name.split('/')
        if obj[0]==song:
            count+=1
            if obj[1]==songType:
                file=client.get_object(bucket_name_op,f'/{song}/{songType}',f'./{song}/{songType}')
                client.remove_object(bucket_name_op,f"/{song}/{songType}")
                count-=1
                flag=True
                rlogs.rpush('logging',f'REST-R: 1. {songType} removed; {count} count; {total_songs} tSongs')
    if count==0:
        total_songs_t=total_songs
        for i in range(int(total_songs)):
            hash=rKV.lpop('allSongs').decode('utf-8')
            if hash!=song:
                rKV.rpush('allSongs',hash)
            else:
                total_songs_t-=1
        rlogs.rpush('logging',f'REST-R: 2.{total_songs-total_songs_t} Removed.')
        total_songs=total_songs_t
    res=0
    if flag==True:
        song_f=open(f'{songType}','wb')
        for data in file:
            song_f.write(data)
        song_f.close()
        response = {f"{songType}":base64.b64encode(open(f'{songType}',"rb").read()).decode('utf-8')}
    else:
        response = {f"{songType}":str(res)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=5000)