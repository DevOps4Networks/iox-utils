rm -rf *.box ~/.vagrant.d/boxes/iox-dev-vm-virtualbox/; \
rm -rf *.box ~/.vagrant.d/boxes/iox-dev-vm-vmware/; \
packer build -force ubuntu1404.json;\
vagrant box add --force --name "iox-dev-vm-virtualbox" builds/virtualbox-ubuntu1404.box;\
vagrant box add --force --name "iox-dev-vm-vmware" builds/vmware-ubuntu1404.box
