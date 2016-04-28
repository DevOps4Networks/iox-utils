#! /usr/bin/env python
# encoding: utf-8
"""
Copyright 2016 Nathan John Sowatskey

This is a sample settings script for the Cisco Fog Director REST API.

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
server_ip = "192.168.153.128"
url_base = "https://%s/api/v1/appmgr/" % server_ip
user_name = 'admin'
password = 'cisco123'
verify = False