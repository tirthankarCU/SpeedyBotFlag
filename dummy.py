#!/usr/bin/env python3

import base64
import glob
import json
import os
import sys

import jsonpickle
import requests

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST = os.getenv("REST") or "localhost:5000"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##

def mkReq(reqmethod, endpoint, data, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data.keys()}")
        print(f"mp3 is of type {type(data['mp3'])} and length {len(data['mp3'])} ")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

#CMD -> python3 dummy.py localhost add 
if len(sys.argv) < 6:
    host = sys.argv[1]
    cmd = sys.argv[2]
    addr = f"http://{host}"
    headers = {'content-type': 'application/json'}
    if cmd=='add':
        add_url = addr + f"/apiv1/add/{sys.argv[3]}/{sys.argv[4]}"
        print(add_url)
        response = requests.post(add_url, headers=headers)
        hash=json.loads(response.text)
        print(hash)
    if cmd=='fetch':
        fetch_url=addr + f"/apiv1/fetch/{sys.argv[3]}"
        print(fetch_url)
        response = requests.post(fetch_url, headers=headers)
        print(f'SUM - {json.loads(response.text)}')

sys.exit(0)