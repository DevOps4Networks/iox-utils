#! /usr/bin/env python
# encoding: utf-8
"""
Copyright 2016 Nathan John Sowatskey

These are sample functions for the Cisco Fog Director REST API.

See: 

http://www.cisco.com/c/en/us/td/docs/routers/access/800/software/guides/iox/fog-director/reference-guide/1-0/fog_director_ref_guide.html

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import requests
import settings
import logging
from logging.config import fileConfig
fileConfig('../etc/logging_config.ini')
logger = logging.getLogger()    

def get_token():

    response = requests.post(settings.url_base + 'tokenservice', 
                            auth=(settings.user_name, settings.password), 
						      verify=False)
                              
    if response.status_code == 202:
        return response.json()['token']
    else:
        logger.error("Response code was - " + response.status_code + " in get_token()")
        return None
    
def get_devices(limit=10, offset=0):
    #The limit default seems to be 10
    
    token = get_token()

    headers = {'x-token-id':token}

    function_part = "devices" + '?limit=' + str(limit) +'&offset=' + str(offset)  

    response = requests.get(settings.url_base + function_part, headers=headers, 
                            verify=settings.verify)

    token = ""

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("Response code was - " + str(response.status_code) + " in get_devices()")
        return None

def delete_device(deviceId):

    token = get_token()

    headers = {'x-token-id':token}

    response = requests.delete(settings.url_base + 'devices/' + deviceId, headers=headers, 
                              verify=settings.verify)
    
    token = ""
    
    return response.status_code

def add_devices_from_file(filename):

    token = get_token()

    headers = {'x-token-id':token}

    files = {'file': open(filename, 'rb')}

    response = requests.post(settings.url_base + 'devices/import', headers=headers, files=files, 
                             verify=settings.verify)
    
    token = ""
    
    return response.status_code