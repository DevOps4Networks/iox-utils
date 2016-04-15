rm -rf ~/.vagrant.d/boxes/iox-dev-vm-virtualbox/; \
rm -rf ~/.vagrant.d/boxes/iox-dev-vm-vmware/; \
rm -rf builds/*.box; \
packer build -force ubuntu1404.json;\
vagrant box add --force --name "iox-dev-vm-virtualbox" builds/virtualbox-ubuntu1404.box;\
vagrant box add --force --name "iox-dev-vm-vmware" builds/vmware-ubuntu1404.box; \
rm -rf builds/*.box
