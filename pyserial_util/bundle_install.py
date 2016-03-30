#! /usr/bin/env python
# encoding: utf-8
"""
This script is intended to be used to automate the installation of IOx bundles 
and GOS images via a console connection to devices that support Cisco's IOx platform. 

It assumes that there are one or more devices connected, typically via a mini-USB
cable, to the machine upon which this script is running. For example, a MacBookPro
with three such devices connected with a USB hub.

The script also assumes that the devices have been previously configured with IP
connectivity using configurations from here, and the scripts from here. IP
connectivity is required for purposes of using TFTP to copy images to the devices.

Finally, there must be a TFTP server at the IP address specified in the tftp_server
variable below. The configuration and equipment required to create that 
arrangement will vary according to circumstances. See this article for an example
of how this can all work.

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
from pyserial_util.cli_utils import *

usb_port_base = "/dev/cu.SLAB_USBtoUART"
usb_port_numbers = [10]
tftp_server = "192.168.1.2"
bundle_name = "ir800-universalk9-bundle.SPA.156-1.T1.bin"
image_name = "ir800-universalk9-mz.SPA.156-1.T1"
gos_vm_name = "ir800-ioxvm-1.0.0.4-T.bin"
enable_password = "cisco123"
            
def install_bundle(serial_port):
    
    logger.info("\nInstalling " + bundle_name + " from flash.")
    
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("bundle install flash:/" + bundle_name + "\r")
        
    while True:
        time.sleep(10)
        serial_port.write("\r")
        response = serial_port.read(serial_port.inWaiting())
        logger.info("The response is " + response + " whilst installing the bundle " + bundle_name + ".")
        if (strip_cr_nl(response).endswith("#")):
            logger.info("Back to # prompt, carrying on.")
            break
        
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("write memory\r")
        time.sleep(1)
        
    return 0

def set_boot_image(serial_port):

    logger.info("\nSetting boot image to " + image_name + " from flash.")
    
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("configure terminal\r")
            
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("(config)#")):   
        serial_port.write("boot system flash:/" + image_name + "\r")
        time.sleep(1)
        response = serial_port.read(serial_port.inWaiting())
        if ("Invalid" in response):
            logger.error("The response contains \"Invalid\" in set_boot_image, returning.")
            return 1
    
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("(config)#")):
        serial_port.write("end\r")
    
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("write memory\r")
        time.sleep(1)
        
    return 0

def install_gos_image(serial_port):

    logger.info("\nInstalling " + gos_vm_name + " from flash.")
    
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("guest-os 1 image install flash:/" + gos_vm_name + " verify\r")
        time.sleep(1)
        response = serial_port.read(serial_port.inWaiting())
        if ("Inappropriate image type" in response):
            logger.error("The response contains \"Inappropriate image type\" in install_gos_image, returning.")
            return 1
        
    while True:
        time.sleep(10)
        response = serial_port.read(serial_port.inWaiting())
        logger.info("The response is " + response + " whilst installing the GOS image " + gos_vm_name + ".")
        if (strip_cr_nl(response).endswith("#")):
            logger.info("Back to # prompt, carrying on.")
            break
                
    serial_port.write("\r")
    time.sleep(1)
    response = serial_port.read(serial_port.inWaiting())
    logger.info(response)
    if (strip_cr_nl(response).endswith("#")):
        serial_port.write("write memory\r")
        time.sleep(1)
        
    return 0
    
def main(argv=None):
       
    for port_number in usb_port_numbers:
        
        usb_port = usb_port_base + str(port_number)
        
        try:
            serial_port = serial.Serial(usb_port,
                                baudrate = 9600,
                                bytesize = serial.EIGHTBITS,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE)
    
        except serial.SerialException as e:
            """
            You may see an exception message such as: "[Errno 16] Resource busy: '/dev/cu.SLAB_USBtoUART6'".
        
            You can try the following to release the resource.
        
            $ lsof | grep UART
            screen    2786          <username>    5u      CHR              17,13      0t189                 725 /dev/cu.SLAB_USBtoUART6
            $ kill -9 2786
            $ sudo lsof | grep UART
            $ 
            """
    
            logger.error("Port " + usb_port + " not available - %s" % e)
            continue
    
        if serial_port.isOpen():
        
            retcode = enable(serial_port, enable_password)
            if (retcode > 0):
                logger.error("enable for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
            
            retcode = set_logging_console(serial_port, False)
            if (retcode > 0):
                logger.error("set_logging_console False for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
    
            retcode = copy_tftp_flash(serial_port, bundle_name, tftp_server)
            if (retcode > 0):
                logger.error("copy_tftp_flash for " + usb_port + " and " + bundle_name + " returned non-zero result " + str(retcode) + ".")
                continue
            
            retcode = copy_tftp_flash(serial_port, gos_vm_name, tftp_server)
            if (retcode > 0):
                logger.error("copy_tftp_flash for " + usb_port + " and " + gos_vm_name + " returned non-zero result " + str(retcode) + ".")
                continue
                        
            retcode = install_bundle(serial_port)
            if (retcode > 0):
                logger.error("install_bundle for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
            
            retcode = set_boot_image(serial_port)
            if (retcode > 0):   
                logger.error("set_boot_image for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
            
            retcode = install_gos_image(serial_port)
            if (retcode > 0):
                logger.error("install_gos_image for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
            
            retcode = set_logging_console(serial_port, True)
            if (retcode > 0):
                logger.error("set_logging_console True for " + usb_port + " returned non-zero result " + str(retcode) + ".")
                continue
    
            reload_device(serial_port)
        
        else:
            logger.error("Serial port " + serial_port + " not open.")
            continue
                
    return 0
     
if __name__ == "__main__":
    sys.exit(main())
