import os
import redis 
from minio import Minio

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

while True:
    hash=rKV.brpop('MSGQ')[1].decode('utf-8')
    rlogs.rpush('logging',f'WORKER: 1. Hashed Hash {hash}')
    file=client.get_object(bucket_name_ip,f'{hash}.dat',f'{bucket_name_ip}/{hash}.dat')
    rlogs.rpush('logging',f'WORKER: 2. Min.io')
    for data in file:
        sdata=data.decode('utf-8')
    sum=0
    for x in sdata.split():
        sum+=int(x)
    rlogs.rpush('logging',f'WORKER: 3. Sum {sum}')
    if not client.bucket_exists(bucket_name_op):
        print(f"Create bucket {bucket_name_op}")
        client.make_bucket(bucket_name_op)
    file=open("sum.o",'w')
    file.write(str(sum))
    file.close()
    cmd=f'mkdir -p /{hash}'
    os.system(cmd)
    cmd=f'mv sum.o /{hash}/'
    os.system(cmd)
    rlogs.rpush('logging',f'WORKER: 4. FILE created sum.o')
    client.fput_object(bucket_name_op,f"/{hash}/sum.o",f"./{hash}/sum.o")
    rlogs.rpush('logging',f'WORKER: 5. Pushed to Min.io/result')

cmd='python -m demucs.separate --out /output /app/short-hop.mp3'
# os.system(cmd)


