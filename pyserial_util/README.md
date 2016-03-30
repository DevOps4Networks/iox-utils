#pySerial Utilities for IOx

The scripts here use the [pySerial](https://github.com/pyserial/pyserial) serial interface capabilities to 
automate these common device configuration tasks:

 - [config_load.py](./config_load.py) - Generate a configuration from a template and configure devices so that they 
 have IP connectivity. 
 - [bundle_install.py](./bundle_install.py) - Install bundles and images via TFTP, assuming IP connectivity and an
 available TFTP server.
 - [clear_reload.py](./clear_reload.py) - Use the "clear start" and "reload" commands to reset a device as though the 
 reset button had been used.