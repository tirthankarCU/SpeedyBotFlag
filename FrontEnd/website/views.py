from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import os
from minio import Minio
import io
import time
from io import BytesIO
import requests
import json, jsonpickle
import os
import sys
import threading
REST = os.getenv("REST") or "localhost:9191"

views = Blueprint('views', __name__)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "minioadmin"
minioPasswd = os.getenv("MINIO_PASSWD") or "minioadmin"

# client = Minio(minioHost,
#                 secure=False,
#                 access_key=minioUser,
#                 secret_key=minioPasswd)
# bucketname='posts'


def mkReq(reqmethod, endpoint, data=None, song=False, songType=None, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data}")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = jsonpickle.decode(json.dumps(response.json(), indent=4, sort_keys=True))
        #print(jsonResponse)
        return jsonResponse
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text



def pollForPost(data_):
    counter=1
    while(counter<50):
        counter=counter+1
        jsonResponse=mkReq(requests.get, f"apiv1/fetch",data=data_)
        print(jsonResponse)
        time.sleep(5)





@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('post1')
        print(note,current_user)
        if len(note) < 1:
            flash('Post is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            # content=BytesIO(bytes(note,'utf-8'))
            # key=str(current_user.id)+'/post'+str(time.time())+'.text'
            # size=content.getbuffer().nbytes 

            # if not client.bucket_exists(bucketname):
            #     print(f"Create bucket {bucketname}")
            #     client.make_bucket(bucketname)
            # files_to_add=[ "views.py"]

            # try:
            #     client.put_object(bucketname,key,content,size)
            # except Exception as err:
            #     print("Error when adding files the first time")
            #     print(err)
            data_={}
            data_['user']=current_user.id
            data_['text']=note
            jsonResponse=mkReq(requests.get, f"apiv1/post", data=data_)
            print(jsonResponse['hash'])
            if(jsonResponse['hash']=='ACK'):
                flash('Post published!', category='success')
                db.session.add(new_note)
                db.session.commit()
            else:
                flash('Post has temporarily being withheld', category='error')
                
                # try:
                #     t1 = threading.Thread(target=pollForPost, args=(data_,))
                #     #t1.start()
                # except:
        
                #     print("Error: unable to start thread")
    data_={}
    data_['user']=current_user.id
    print(current_user.id)
    jsonResponse=mkReq(requests.get, f"apiv1/fetch",data=data_)
    print(jsonResponse['data'])
    userPosts=[]
    userPosts = jsonResponse['data'].split('[SEP]')

    return render_template("home.html", user=current_user,userPosts=userPosts)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
