#! /usr/bin/env python
# encoding: utf-8
"""
Copyright 2016 Nathan John Sowatskey

This is a sample test script for the Cisco Fog Director REST API.

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

##Warning!! This is a destructive test that deletes all devices that are in the system. It is intended to be
##used against a test system, NOT a live system.

import iox_fog_dir_rest.functions as functions

#TODO This is a little awkward as the default limit is 10. so this is a hack for now
devices = functions.get_devices(limit=100)

if devices != None:
    data = devices['data']

    for device in data:
        functions.delete_device(device['deviceId'])

    devices = functions.get_devices(limit=100)
    data = devices['data']
    assert(len(data) == 0)
    
functions.add_devices_from_file("../etc/twoSampleDevices.csv")
devices = functions.get_devices()
data = devices['data']

assert(len(data) == 2)

for device in data:
    functions.delete_device(device['deviceId'])

devices = functions.get_devices()
data = devices['data']
assert(len(data) == 0)

#TODO In this case the second device with the same address overwrites the first, and the 
#return code is 200, which is perhaps not correct?
assert(functions.add_devices_from_file("../etc/identicalIPAddrSampleDevices.csv") == 200)
devices = functions.get_devices()
data = devices['data']
for device in data:
    functions.delete_device(device['deviceId'])

functions.add_devices_from_file("../etc/25SampleDevices.csv")
devices = functions.get_devices(limit=100)
data = devices['data']
assert(len(data) == 25)

#TODO Host name or IP address seems to be a key, but the order of the results is not in order of either
#of those two values it seems. The results don't seem to match the UI either.
devices = functions.get_devices(limit=15)
data = devices['data']
assert(len(data) == 15)

#TODO, this is not working.
devices = functions.get_devices(limit=5, offset=15)
data = devices['data']
assert(len(data) == 5)

devices = functions.get_devices(limit=5, offset=20)
data = devices['data']
assert(len(data) == 5)

devices = functions.get_devices(limit=5, offset=25)
data = devices['data']
assert(len(data) == 0)