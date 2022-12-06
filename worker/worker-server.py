import os
import redis 
from minio import Minio
from detoxify import Detoxify

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

# RETURNS true if it's safe
def checkWithBert(sen):
    results = Detoxify('original').predict(sen)
    cnt=0
    for k,v in results.items():
        if v>0.7:
            cnt+=1
    if cnt>=2:
        return False
    return True

load_wts=Detoxify('original').predict('some text')
while True:
    ResponseError=None
    hash=rKV.brpop('bad')[1].decode('utf-8')
    rlogs.rpush('logging',f'WORKER: 1. File {hash}')
    file=client.get_object(bucket_name_ip2,f'{hash}',f'{bucket_name_ip2}/{hash}')
    rlogs.rpush('logging',f'WORKER: 2. Min.io')
    sen=''
    for data in file:
        sen+=data.decode('utf-8')
    if checkWithBert(sen)==True:
        try:
            client.fput_object(bucket_name_ip1,f"/{hash}",f"./{hash}")
            user=hash.split('.')[1]
            if rKV.exists(user)==True:
                value=rKV.get(user).decode('utf-8')
                value=value+';'+f"{hash}"
                rKV.set(user,value)
            else:
                rKV.set(user,f"{hash}")
            rlogs.rpush('logging',f'WORKER: 3. tweet is safe.')
        except ResponseError as err:
            print("Error when adding files.")
            print(err)
    else:
        rlogs.rpush('logging',f'WORKER: 3. tweet is not safe.')



