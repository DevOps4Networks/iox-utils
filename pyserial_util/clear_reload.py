#! /usr/bin/env python
# encoding: utf-8
"""
This script is intended to be used to automate the process of
clearing configurations and reloading, via a console connection, 
for devices that support Cisco's IOx platform. 

The outcome is a device that has no startup configuration, and which has
been booted from rommon-2 for a given image. This is the software equivalent
of using the reset button.

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
import getopt
import logging
from logging.config import fileConfig
import os
from pyserial_util.cli_utils import *

usb_port_base = "cu.SLAB_USBtoUART"
password = "cisco123"
    
def main(argv=None):
    
    boot_image = "ir800-universalk9-mz.SPA.156-1.T1"
      
    device_serial_ports = get_console_ports(usb_port_base)
    
    for dev_ser_port in device_serial_ports:        
        logger.info("Working with a " + dev_ser_port.device_type + " at " + dev_ser_port.serial_port.port + " to clear startup configuration and reload.")
                    
        if enable(dev_ser_port.serial_port, password) == 0:

            dev_ser_port.serial_port.write("clear start\r")            
            time.sleep(1)
            response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
            logger.debug(response)
            if "[confirm]" in response:
                dev_ser_port.serial_port.write("\r")            
                time.sleep(1)
                dev_ser_port.serial_port.write("\r")            
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
            
            if response.endswith("#"):
                dev_ser_port.serial_port.write("reload\r")            
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
           
            if "Do you want to reload the internal AP ? [yes/no]:" in response:
                dev_ser_port.serial_port.write("yes\r")            
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
                
            if "Do you want to save the configuration of the AP? [yes/no]" in response:
                dev_ser_port.serial_port.write("no\r")            
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
            
            if "Proceed with reload? [confirm]" in response:
                dev_ser_port.serial_port.write("\r")            
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
                    
    time.sleep(60)
    
    for dev_ser_port in device_serial_ports:        
        logger.info("Working with a " + dev_ser_port.device_type + " at " + dev_ser_port.serial_port.port + " to boot from rommon-2.")
        
        while True:
            dev_ser_port.serial_port.write("\r")            
            time.sleep(1)
            response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
            logger.debug(response)
            if "rommon-2>" in response:
                dev_ser_port.serial_port.write("boot flash:/" + boot_image + "\r")            
                time.sleep(1)
                response = strip_cr_nl(dev_ser_port.serial_port.read(dev_ser_port.serial_port.inWaiting()))
                logger.debug(response)
                break
             
    return 0
     
if __name__ == "__main__":
    sys.exit(main())
