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
from pyserial_util.cli_utils import *

usb_port_base = "cu.SLAB_USBtoUART"
bundle_name = "ir800-universalk9_npe-bundle.SPA.156-2.T.bin"
image_name = "ir800-universalk9_npe-mz.SPA.156-2.T"
#If the GOS is bundled,and not being updated separately, then leave this string empty
#gos_vm_name = "ir800-ioxvm-1.0.0.4-T.bin"
gos_vm_name = "ir800-ioxvm.20160404.bin"
enable_password = "cisco123"

def get_network_from_host_name(dev_ser_port):
   
    network = ""
    
    logger.info("\nInstalling " + bundle_name + " from flash.")
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)

    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("show running-config | begin hostname\r")
        time.sleep(1)
        response = dev_ser_port.read(dev_ser_port.inWaiting())
        logger.debug(response)
        index_start = response.find("SN")
        index_end = response.find("EN")
        network = response[index_start+2:index_end]
        
    return network
            
def install_bundle(dev_ser_port):
    
    logger.info("\nInstalling " + bundle_name + " from flash.")
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)

    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("bundle install flash:/" + bundle_name + "\r")
        
    while True:
        time.sleep(10)
        dev_ser_port.write("\r")
        response = dev_ser_port.read(dev_ser_port.inWaiting())
        logger.info("The response is " + response + " whilst installing the bundle " + bundle_name + ".")
        if (strip_cr_nl(response).endswith("#")):
            logger.info("Back to # prompt, carrying on.")
            break
        
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)

    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("write memory\r")
        time.sleep(1)
        
    return 0

def set_boot_image(dev_ser_port):

    logger.info("\nSetting boot image to " + image_name + " from flash.")
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("configure terminal\r")
            
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("(config)#")):   
        dev_ser_port.write("boot system flash:/" + image_name + "\r")
        time.sleep(1)
        response = dev_ser_port.read(dev_ser_port.inWaiting())
        if ("Invalid" in response):
            logger.error("The response contains \"Invalid\" in set_boot_image, returning.")
            return 1
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("(config)#")):
        dev_ser_port.write("end\r")
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("write memory\r")
        time.sleep(1)
        
    return 0

def remove_gos_image(dev_ser_port):

    logger.info("\Stopping and uninstalling existing GOS image.")
    
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("guest-os 1 stop\r")
    
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("guest-os 1 image uninstall\r")

    return 0

def install_gos_image(dev_ser_port):

    logger.info("\nInstalling " + gos_vm_name + " from flash.")
        
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)
    if (strip_cr_nl(response).endswith("#")):    
        dev_ser_port.write("guest-os 1 image install flash:/" + gos_vm_name + " verify\r")
        time.sleep(1)
        response = dev_ser_port.read(dev_ser_port.inWaiting())
        if ("Inappropriate image type" in response):
            logger.error("The response contains \"Inappropriate image type\" in install_gos_image, returning.")
            return 1
        
    while True:
        time.sleep(10)
        response = dev_ser_port.read(dev_ser_port.inWaiting())
        logger.info("The response is " + response + " whilst installing the GOS image " + gos_vm_name + ".")
        if (strip_cr_nl(response).endswith("#")):
            logger.info("Back to # prompt, carrying on.")
            break
                
    dev_ser_port.write("\r")
    time.sleep(1)
    response = dev_ser_port.read(dev_ser_port.inWaiting())
    logger.debug(response)

    if (strip_cr_nl(response).endswith("#")):
        dev_ser_port.write("write memory\r")
        time.sleep(1)
        
    return 0
    
def main(argv=None):
    
    device_serial_ports = get_console_ports(usb_port_base)
        
    logger.info("About to start on these serial ports - " + str(device_serial_ports))
    
    summary = []
       
    for dev_ser_port in device_serial_ports:
        
        retcode = enable(dev_ser_port.serial_port, enable_password)
        if (retcode > 0):
            logger.error("enable for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                         + str(retcode) + ".")
            continue
        
        network = get_network_from_host_name(dev_ser_port.serial_port)
        tftp_server = network.replace(".0", ".2")
        
        retcode = set_logging_console(dev_ser_port.serial_port, False)
        if (retcode > 0):
            logger.error("set_logging_console False for " + dev_ser_port.serial_port.port 
                         + " returned non-zero result " + str(retcode) + ".")
            continue

        if bundle_name:
            retcode = copy_tftp_flash(dev_ser_port.serial_port, bundle_name, tftp_server)
            if (retcode > 0):
                logger.error("copy_tftp_flash for " + dev_ser_port.serial_port.port + " and " + bundle_name 
                             + " returned non-zero result " + str(retcode) + ".")
                continue
        
        if gos_vm_name: 
            retcode = copy_tftp_flash(dev_ser_port.serial_port, gos_vm_name, tftp_server)
            if (retcode > 0):
                logger.error("copy_tftp_flash for " + dev_ser_port.serial_port.port + " and " + gos_vm_name 
                             + " returned non-zero result " + str(retcode) + ".")
                continue
        
        retcode = remove_gos_image(dev_ser_port.serial_port)
        if (retcode > 0):
            logger.error("remove_gos_image for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                         + str(retcode) + ".")
            continue
                 
        if bundle_name:   
            retcode = install_bundle(dev_ser_port.serial_port)
            if (retcode > 0):
                logger.error("install_bundle for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                             + str(retcode) + ".")
                continue
        
        if image_name:
            retcode = set_boot_image(dev_ser_port.serial_port)
            if (retcode > 0):   
                logger.error("set_boot_image for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                             + str(retcode) + ".")
                continue
         
        if gos_vm_name: 
            retcode = install_gos_image(dev_ser_port.serial_port)
            if (retcode > 0):
                logger.error("install_gos_image for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                             + str(retcode) + ".")
                continue
        
        retcode = set_logging_console(dev_ser_port.serial_port, True)
        if (retcode > 0):
            logger.error("set_logging_console True for " + dev_ser_port.serial_port.port + " returned non-zero result " 
                         + str(retcode) + ".")
            continue

        reload_device(dev_ser_port.serial_port)
        
        summary.append("Installed bundles and images for a " + dev_ser_port.device_type + " at " 
                       + dev_ser_port.serial_port.port + ".\n")
             
    logger.info("The summary is:\n")
    for result in summary:
        logger.info(str(result) + "\n")
   
    return 0
     
if __name__ == "__main__":
    sys.exit(main())
