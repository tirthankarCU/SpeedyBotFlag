import os
import redis 
from minio import Minio

redisHost = os.getenv("REDIS_HOST") or "redis-svc"
redisPort = os.getenv("REDIS_PORT") or 6000

minioHost = os.getenv("MINIO_HOST") or "minio-svc"
minioUser = os.getenv("MINIO_USER") or "root"
minioPasswd = os.getenv("MINIO_PASSWD") or "root123"
client = Minio(minioHost,secure=False,access_key=minioUser,secret_key=minioPasswd)

cmd='mkdir -p RANDI'
os.system(cmd)

rKV=redis.Redis(host=redisHost,port=redisPort)
while True:
    data=rKV.brpop('MSGQ')
    file=open('op.txt','w')
    print(data[1].decode('utf-8'))
    file.write(data[1].decode('utf-8'))
    file.close()
    break
    # msg=client.fget_object('my-bucket',hash)

cmd='mkdir -p RANDI2'
os.system(cmd)

cmd='python -m demucs.separate --out /output short-hop.mp3'
os.system(cmd)


