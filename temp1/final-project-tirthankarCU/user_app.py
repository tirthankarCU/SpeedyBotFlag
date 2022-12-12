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

def mkReq(reqmethod, endpoint, data=None, song=False, songType=None, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data}")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = jsonpickle.decode(json.dumps(response.json(), indent=4, sort_keys=True))
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
    if cmd=='post':
        data_={}
        data_['user']=sys.argv[2]
        data_['text']=sys.argv[3]
        mkReq(requests.get, f"apiv1/post", data=data_)
    elif cmd=='fetch':
        data_={}
        data_['user']=sys.argv[2]
        mkReq(requests.get, f"apiv1/fetch",data=data_)
    else:
        print(f'wrong api endpoint.')

sys.exit(0)