#!/usr/bin/env python3

import requests
import json, jsonpickle
import os
import sys
import base64
import glob


#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST = os.getenv("REST") or "localhost:80"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##

def mkReq(reqmethod, endpoint, data, song=False, songType=None, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data.keys()}")
        print(f"mp3 is of type {type(data['mp3'])} and length {len(data['mp3'])} ")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = jsonpickle.decode(json.dumps(response.json(), indent=4, sort_keys=True))
        if song==True:
            jsonData=jsonResponse[f'{songType}']
            song=base64.b64decode(jsonData)
            song_f=open(f'{songType}','wb')
            song_f.write(song)
            song_f.close()
        else:
            jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
            print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

if len(sys.argv) <= 4:
    host = REST
    cmd = sys.argv[1]
    addr = f"http://{host}"
    headers = {'content-type': 'application/json'}
    if cmd=='separate':
        for mp3 in glob.glob("data/*.mp3"):
            if mp3.split('/')[1]!=sys.argv[2]:
                continue
            print(f"Step 1: /{mp3}")
            mkReq(requests.post, "apiv1/separate",
                data={
                    "mp3": base64.b64encode( open(mp3, "rb").read() ).decode('utf-8'),
                    "callback": {
                        "url": "http://localhost:5000",
                        "data": {"mp3": mp3, 
                                "data": "to be returned"}
                    }
                },
                verbose=True
                )
    elif cmd=='queue':
        print(f"Step 2:")
        mkReq(requests.get, "apiv1/queue", data=None)
    elif cmd=='track':
        mkReq(requests.get, f"apiv1/track/{sys.argv[2]}/{sys.argv[3]}",song=True,songType=sys.argv[3],data=None)
    elif cmd=='remove':
        print(f"Step 4:")
        mkReq(requests.get, f"apiv1/remove/{sys.argv[2]}/{sys.argv[3]}",song=True,songType=sys.argv[3],data=None)
    else:
        print(f'wrong api endpoint.')

sys.exit(0)