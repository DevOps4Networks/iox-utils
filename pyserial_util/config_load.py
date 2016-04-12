#! /usr/bin/env python
# encoding: utf-8
"""
This script is intended to be used to automate the application of
configurations, via a console connection, for devices that 
support Cisco's IOx platform. 

It assumes that there are one or more devices connected, typically via a mini-USB
cable, to the machine upon which this script is running. For example, a MacBookPro
with three such devices connected with a USB hub.

The script uses pyserial to connect to the serial ports and carry out a set of 
interactions. The style is very reminiscent of "expect". That also means, though,
that things don't always work as expected because the CLI wasn't really meant for
automation like this, hence the copious logging. 

Note that these drivers will likely be required for pyserial:

https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx#mac

Copyright 2016 Nathan John Sowatskey

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
from __future__ import print_function

import serial
import time
import sys
import logging
from logging.config import fileConfig
import os
from pyserial_util.cli_utils import *

usb_port_base = "cu.SLAB_USBtoUART"
enable_password = "cisco123"
    
def main(argv=None):
      
    device_serial_ports = get_console_ports(usb_port_base)
        
    logger.info("About to start on these serial ports and devices:\n")
    for dev_ser_port in device_serial_ports:
        logger.info("Port = " + str(dev_ser_port.serial_port) + " device type = " + 
                    str(dev_ser_port.device_type) + "\n")
    
    summary = []
    
    device_counter = 1
    first_net_tuple = "10"
    second_net_tuple = 42
    lan_dhcp_upper = "2"
    process_images = False
    
    for dev_ser_port in device_serial_ports:
        skip_device = False
        
        logger.info("Configuring a " + dev_ser_port.device_type + " at " + dev_ser_port.serial_port.port + ".")

        config = []        
        try:
            with open("configs/" + dev_ser_port.device_type + ".cfgtmpl") as config_file:
                for line in config_file:
                    config.append(line)
        except Exception as e:
            logger.error("%s" % e)
            continue      
                    
        enable(dev_ser_port.serial_port, enable_password)
            
        #TODO Refactor to device info class 
        num_ports = {'IR829GW-LTE-GA-EK9' : 4, 'IR809G-LTE-GA-K9' : 2}[dev_ser_port.device_type]

        lan_dhcp_upper = str(1+num_ports)
    
        for line in config:
            
            if line.startswith("!"):
                continue
                        
            original_line = line
            
            line = line.replace("<NT1>", first_net_tuple)
            line = line.replace("<NT2>", str(second_net_tuple))
            line = line.replace("<LDU>", lan_dhcp_upper)
            
            if (process_images):
                if ("#Process images:" in line):
                    line = line.replace("#Process images:", "")
        
            if (line != original_line):
                logger.debug("Processed config line is " + line)
             
            if (line.startswith("hostname")):
                line = strip_cr_nl(line) + "-SN" + first_net_tuple + "." + str(second_net_tuple) + ".1.0EN"  
            
            dev_ser_port.serial_port.write(line)
        
            while True:
                dev_ser_port.serial_port.write("\r")
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug("The response is " + response + " whilst adding configuration.")
                if "Invalid" in response:
                    logger.error("The response contained \"Invalid\", which is not OK, so returning.")
                    return 1
                if (response.endswith("#")):
                    logger.debug("Back to # prompt, carrying on.")
                    break
                if (response.endswith(">")):
                    logger.error("We have a > prompt, which is not OK, so skipping this device.")
                    skip_device = True
                    break
            
            if(skip_device):
                break
          
        if not skip_device:
            dev_ser_port.serial_port.write("write memory\r")
            time.sleep(1)
            second_net_tuple += 1
            device_counter += 1
            summary.append("Configured a " + dev_ser_port.device_type + " at " + dev_ser_port.serial_port.port + ".")

    logger.info("The summary is:\n")
    for result in summary:
        logger.info(str(result) + "\n")
                
    return 0
     
if __name__ == "__main__":
    sys.exit(main())
