#! /usr/bin/env python
# encoding: utf-8
"""
This set of commands will, given the appropriately set up infrastructure, obtain and install new IOx bundles and 
GOS VMs, via a serial connection to the mini-USB usb_port.

If your settings differ, then just edit this script directly.

Note that these drivers will likely be required for pyserial:

https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx#mac

"""
from __future__ import print_function

import sys
sys.path.insert(0, '..')

import serial
import time
import sys
import getopt

"""

To obtain the appropriate USB device, try the following, noting that the last number seems subject to change:

ls /dev/cu*
... /dev/cu.SLAB_USBtoUART6

"""
usb_port = "/dev/cu.SLAB_USBtoUART1"
tftp_server = "192.168.1.2"
bundle_name = "ir800-universalk9-bundle.SPA.156-1.T1.bin"
image_name = "ir800-universalk9-mz.SPA.156-1.T1a"
gos_vm_name = "ir800-ioxvm-1.0.0.4-T.bin"
password = "cisco123"

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
    
def enable(ser):
    
    print("\nEntering enable mode.")

    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith(">")):
        ser.write("enable\r")
    else:
        if (response.endswith("#")):
            print("We are in enable mode.")
            return 0;
        else:
            print("The response did not end in \">\" or \"#\", which is not OK, exiting.")
            return 2
        
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith("Password: ")):
        ser.write(password)
    else:
        print("The response did not end in \"Password: \", but that is OK.")
        
    return 0
        
def copy_tftp_flash(ser, filename):
    
    print("\nCopying " + filename + " from tftp to flash.")
    
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith("#")):
        ser.write("copy tftp flash\r")
        time.sleep(1)
    else:
        print("The response did not end in \"#\", so probably not in enable mode, exiting.")
        return 2
 
    response = ser.read(ser.inWaiting())
    print(response)
    if ("Address or name of remote host" in response):
        ser.write(tftp_server + "\r")
        time.sleep(1)
    else:
        print("The response did not contain \"Address or name of remote host\", so probably not where we need to be, exiting.")
        return 2
     
    response = ser.read(ser.inWaiting())
    print(response)
    if ("Source filename" in response):
        ser.write(filename + "\r")
        time.sleep(1)
    else:
        print("The response did not contain \"Source filename\", so probably not where we need to be, exiting.")
        return 2
      
    response = ser.read(ser.inWaiting())
    print(response)
    if ("Destination filename" in response):
        ser.write(filename + "\r")
        time.sleep(1)
    else:
        print("The response did not contain \"Destination filename\", so probably not where we need to be, exiting.")
        return 2
        
    response = ser.read(ser.inWaiting())
    print(response)
    if ("already existing" in response):
        print("The response did contain \"already existing\", which is OK, and it shall be overwritten.")
        ser.write("\r")
        time.sleep(1)
        
    response = ser.read(ser.inWaiting())
    print(response)
    if ("Accessing" in response):
        print("Copy from tftp server " + tftp_server + " of file " + filename + " started.")

    while True:
        time.sleep(10)
        response = ser.read(ser.inWaiting())
        print("The response is " + response + " whilst accessing the file " + filename + ".")
        if (response.endswith("#")):
            print("Back to # prompt, carrying on.")
            break
    
    if ("Error" in response):
        print("The response contained the word \"Error\", which is not good, exiting.")
        return 2
    
    return 0
        
def install_bundle(ser):
    
    print("\nInstalling " + bundle_name + " from flash.")
    
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (strip_cr_nl(response).endswith("#")):
        ser.write("bundle install flash:/" + bundle_name + "\r")
        time.sleep(1)
        
    while True:
        time.sleep(10)
        response = ser.read(ser.inWaiting())
        print("The response is " + response + " whilst installing the bundle " + bundle_name + ".")
        if (response.endswith("#")):
            print("Back to # prompt, carrying on.")
            break
        
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith("#")):
        ser.write("write memory\r")
        time.sleep(1)
        
    return 0

def set_boot_image(ser):

    print("\nSetting boot image to " + image_name + " from flash.")
    
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (strip_cr_nl(response).endswith("#")):
        ser.write("boot system flash:/" + image_name + "\r")
        time.sleep(1)
        
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith("#")):
        ser.write("write memory\r")
        time.sleep(1)
        
    return 0

def install_gos_image(ser):

    print("\nInstalling " + gos_vm_name + " from flash.")
    
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (strip_cr_nl(response).endswith("#")):
        ser.write("guest-os 1 image install flash:/" + gos_vm_name + "\r")
        time.sleep(1)
        
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (response.endswith("#")):
        ser.write("write memory\r")
        time.sleep(1)
        
    return 0

def reload(ser):
    
    print("\nReloading.")
    
    ser.write("\r")
    time.sleep(1)
    response = ser.read(ser.inWaiting())
    print(response)
    if (strip_cr_nl(response).endswith("#")):
        ser.write("reload\r")
        time.sleep(1)
        
    response = ser.read(ser.inWaiting())
    print(response)
    if ("yes/no" in strip_cr_nl(response)):
        ser.write("yes\r")
        time.sleep(1)
        
    response = ser.read(ser.inWaiting())
    print(response)
    if ("yes/no" in strip_cr_nl(response)):
        ser.write("yes\r")
        time.sleep(1)
        
    return 0
        
def strip_cr_nl(str):
    str.replace("\r", "")
    str.replace("\n", "")
    return str
    
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
             raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
        
    try:
        ser = serial.Serial(usb_port,
                            baudrate = 9600,
                            bytesize = serial.EIGHTBITS,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE)

    except serial.SerialException as e:
        """
        You may see an exception message such as: "[Errno 16] Resource busy: '/dev/cu.SLAB_USBtoUART6'".
    
        You can try the following to release the resource.
    
        $ sudo lsof | grep UART
        screen    2786          <username>    5u      CHR              17,13      0t189                 725 /dev/cu.SLAB_USBtoUART6
        $ kill -9 2786
        $ sudo lsof | grep UART
        $ 
        """

        print("Port " + usb_port + " not available - %s" % e)
        return 2

    if ser.isOpen():
    
        retcode = enable(ser)

        if (retcode == 0):
            retcode = copy_tftp_flash(ser, bundle_name)
        else:
            return retcode
        
        if (retcode == 0):
            retcode = copy_tftp_flash(ser, gos_vm_name)
        else:
            return retcode
        
        if (retcode == 0):
            retcode = install_bundle(ser)
        else:
            return retcode
        
        if (retcode == 0):
            retcode = set_boot_image(ser)
        else:
            return retcode
        
        if (retcode == 0):
            retcode = install_gos_image(ser)
        else:
            return retcode

        if (retcode == 0):
            retcode = reload(ser)
            
        return 0
     
if __name__ == "__main__":
    sys.exit(main())
