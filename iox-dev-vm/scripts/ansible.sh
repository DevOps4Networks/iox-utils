#!/bin/bash -eux

# Install Ansible repository.
apt-get -y update && apt-get -y upgrade
apt-get -y install software-properties-common
apt-add-repository ppa:ansible/ansible

# Install Ansible and Git.
apt-get -y update
apt-get -y install ansible git

#Install a key for VMware repo
wget https://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub
apt-key add VMWARE-PACKAGING-GPG-RSA-KEY.pub
wget https://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub
apt-key add VMWARE-PACKAGING-GPG-DSA-KEY.pub

#Add VMware repo
apt-add-repository 'deb http://packages.vmware.com/packages/ubuntu precise main'
apt-get -y update

cat > /tmp/requirements.yml << EOM
- name: ansible-role-packer-debian
  src: https://github.com/DevOps4Networks/ansible-role-packer-debian
- name: geerlingguy.nfs
EOM
sudo ansible-galaxy install --force -r /tmp/requirements.yml
