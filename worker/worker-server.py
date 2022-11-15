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
    hash=rKV.brpop('msgq')[1].decode('utf-8')
    rlogs.rpush('logging',f'WORKER: 1. Hashed Hash {hash}')
    file=client.get_object(bucket_name_ip,f'{hash}.mp3',f'{bucket_name_ip}/{hash}.mp3')
    rlogs.rpush('logging',f'WORKER: 2. Min.io')
    fmp3=open("song.mp3",'wb')
    for data in file:
        fmp3.write(data)
    fmp3.close()
    rlogs.rpush('logging',f'WORKER: 3. Song put in mp3 file')
    cmd='ffmpeg -i song.mp3 song.wav'
    os.system(cmd)
    rlogs.rpush('logging',f'WORKER: 4. mp3 converted to wav')
    if not client.bucket_exists(bucket_name_op):
        print(f"Create bucket {bucket_name_op}")
        client.make_bucket(bucket_name_op)

    cmd=f'mkdir -p /{hash}'
    os.system(cmd)
    cmd='demucs -n mdx_q song.wav'
    os.system(cmd)
    cmd=f'mv separated/mdx_q/song/*.wav /{hash}/'
    os.system(cmd)
    cmd=f'rm -rf *.wav *.mp3 separated'
    os.system(cmd)
    rlogs.rpush('logging',f'WORKER: 4. Linux commands exec.')
    
    try:
        client.fput_object(bucket_name_op,f"/{hash}/bass.wav",f"./{hash}/bass.wav")
        client.fput_object(bucket_name_op,f"/{hash}/vocals.wav",f"./{hash}/vocals.wav")
        client.fput_object(bucket_name_op,f"/{hash}/drums.wav",f"./{hash}/drums.wav")
        client.fput_object(bucket_name_op,f"/{hash}/other.wav",f"./{hash}/other.wav")
    except ResponseError as err:
        print("Error when adding files.")
        print(err)
    rlogs.rpush('logging',f'WORKER: 5. Pushed to Min.io/result')



