#! /usr/bin/env python
# encoding: utf-8
"""
This is a set of utility functions for interacting via a serial console with
device CLI.

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
import logging
import os

from logging.config import fileConfig
fileConfig('logging_config.ini')
logger = logging.getLogger()    


class DeviceSerialPort:
    serial_port = ""
    device_type = ""
    
    def __init__(self, serial_port, device_type):
        self.serial_port = serial_port
        self.device_type = device_type

def get_console_ports(usb_port_base):
    """
    The console ports are assumed to be available under /dev/ on Linux and OS X
    type systems. The format of the name is defined by the usb_port_base variable
    plus a number, up to however many there are connected.

    In practice, not all console ports that appear when looking under /dev/
    will actually connect to a device console. At the time of coding, it is not
    clear how to tell, apart from poking to see what happens.
    
    The result is a list of DeviceSerialPort instances that do seem to
    have a device connected.
    """
    possible_usb_ports_names = []
    for filename in os.listdir("/dev/"):
        logger.debug(filename)
        if (usb_port_base in filename):
            possible_usb_ports_names.append(filename)
            
    logger.info("Possible USB port names are: " + str(possible_usb_ports_names))
    
    possible_usb_ser_ports = []
    for port_name in possible_usb_ports_names:
        try:
            possible_usb_ser_ports.append(serial.Serial("/dev/" + port_name,
                                baudrate = 9600,
                                bytesize = serial.EIGHTBITS,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE))
        
        except serial.SerialException as e:
            logger.error("Port " + port_name + " not available - %s" % e)
            continue
        
    device_serial_ports = []
    for serial_port in possible_usb_ser_ports:
        if serial_port.isOpen():
            serial_port.write("\r")
            time.sleep(1)
            response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
            logger.info(response)
            if (not response):
                logger.debug("The response was empty so " + serial_port.port +" seems not to be connected to a device.")
                continue
            elif ("rommon-2>" in response):
                logger.error("The response contained \"rommon-2>\", so the device at " + serial_port.port +" needs to be booted to IOS with the command: \"boot flash:/<Image Name>\".")
                continue
                #TODO code for rommon-2 boot
            elif ("initial configuration dialog?" in response):
                logger.debug("We have the initial configuration dialog prompt, so it looks like " + serial_port.port + " is connected to a device.")
                serial_port.write("no\r")
                while True:                        
                    serial_port.write("\r")
                    time.sleep(5
                               )
                    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
                    logger.debug("The response is " + response + " after initial configuration dialog.")
                    if response.endswith(">") or response.endswith("#"):
                        logger.info("Back to > or # prompt, carrying on.")
                        break
            elif ("Please answer" in response):
                logger.debug("We have the initial configuration dialog prompt, so it looks like " + serial_port.port + " is connected to a device.")
                serial_port.write("no\r")
                while True:                        
                    serial_port.write("\r")
                    time.sleep(5
                               )
                    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
                    logger.debug("The response is " + response + " after initial configuration dialog.")
                    if response.endswith(">") or response.endswith("#"):
                        logger.info("Back to > or # prompt, carrying on.")
                        break
            elif (response.endswith(">") or response.endswith("#")):
                logger.debug("We have a prompt, so it looks like " + serial_port.port + " is connected to a device.")
                if "config" in response:
                    serial_port.write("end\r")
                    time.sleep(1)
        
            serial_port.write("show hardware | begin Device\r")
            time.sleep(1)
            response = serial_port.read(serial_port.inWaiting())
            logger.debug(response)
            #TODO This regexsy type thing here will need attention
            device_type = "unknown"
            if ("IR829GW-LTE-GA-EK9" in response):
                device_type = "IR829GW-LTE-GA-EK9"
            elif  ("IR809G-LTE-GA-K9" in response):
                device_type = "IR809G-LTE-GA-K9"
            device_serial_ports.append(DeviceSerialPort(serial_port, device_type))
            while True:
                serial_port.write("\r")
                time.sleep(1)
                response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
                logger.debug("The response is " + response + " whilst checking device type.")
                if response.endswith(">") or response.endswith("#"):
                    logger.info("Back to > or # prompt, carrying on.")
                    break
                
    return device_serial_ports
            
def enable(serial_port, enable_password):
    
    logger.info("\nEntering enable mode.")

    serial_port.write("\r")
    time.sleep(1)
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith(">")):
        serial_port.write("enable\r")
        time.sleep(1)
    else:
        if (response.endswith("#")):
            logger.debug("We are in enable mode.")
            return 0;
        else:
            logger.error("The response did not end in \">\" or \"#\", which is not OK, returning.")
            return 1
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.info(response)
    if (response.endswith("Password: ")):
        serial_port.write(enable_password + "\r")
    else:
        logger.debug("The response did not end in \"Password: \", but that is OK.")
        
    return 0

def set_logging_console(serial_port, flag):
    
    logger.info("\nSetting console logging to " + str(flag) + ".")

    serial_port.write("\r")
    time.sleep(1)
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith("#")):
        serial_port.write("configure terminal\r")
        time.sleep(1)
    else:
        logger.error("The response did not end in \"#\", which is not OK, returning.")
        return 1
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith("(config)#")):
        if (flag):
            serial_port.write("logging console\r")
        else:
            serial_port.write("no logging console\r")
    else:
        logger.error("The response did not end in \"(config)#\", which is not OK, returning.")
        return 1
    
    time.sleep(1)    
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith("(config)#")):
        serial_port.write("end\r")
    else:
        logger.error("The response did not end in \"(config)#\", which is not OK, returning.")
        return 1
   
    return 0

def copy_tftp_flash(serial_port, filename, tftp_server):
    
    logger.info("\nCopying " + filename + " from tftp to flash.")
    
    serial_port.write("\r")
    time.sleep(1)
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith("#")):
        serial_port.write("copy tftp flash\r")
        time.sleep(1)
    else:
        logger.error("The response did not end in \"#\", so probably not in enable mode, returning.")
        return 1
 
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("Address or name of remote host" in response):
        serial_port.write(tftp_server + "\r")
        time.sleep(1)
    else:
        logger.error("The response did not contain \"Address or name of remote host\", so probably not where we need to be, returning.")
        return 1
     
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("Source filename" in response):
        serial_port.write(filename + "\r")
        time.sleep(1)
    else:
        logger.error("The response did not contain \"Source filename\", so probably not where we need to be, returning.")
        return 1
      
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("Destination filename" in response):
        serial_port.write(filename + "\r")
        time.sleep(1)
    else:
        logger.error("The response did not contain \"Destination filename\", so probably not where we need to be, returning.")
        return 1
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("already existing" in response):
        logger.debug("The response did contain \"already existing\", which is OK, and it shall be overwritten.")
        serial_port.write("\r")
        time.sleep(1)
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("Accessing" in response):
        logger.debug("Copy from tftp server " + tftp_server + " of file " + filename + " started.")

    while True:
        time.sleep(10)
        response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
        logger.debug("The response is " + response + " whilst accessing the file " + filename + ".")
        if (response.endswith("#")):
            logger.info("Back to # prompt, carrying on.")
            break
    
    if ("Error" in response):
        logger.error("The response contained the word \"Error\", which is not good, returning.")
        return 1
    
    return 0
        
def reload_device(serial_port):
    
    logger.info("\nReloading.")
    
    serial_port.write("\r")
    time.sleep(1)
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if (response.endswith("#")):
        serial_port.write("reload\r")
        time.sleep(1)
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("yes/no" in strip_cr_nl(response)):
        serial_port.write("yes\r")
        time.sleep(1)
        
    response = strip_cr_nl(serial_port.read(serial_port.inWaiting()))
    logger.debug(response)
    if ("yes/no" in strip_cr_nl(response)):
        serial_port.write("yes\r")
        time.sleep(1)
        
    return 0
        
def strip_cr_nl(orig_str):
    new_str = orig_str.replace('\r', '').replace('\n', '')
    return new_str
