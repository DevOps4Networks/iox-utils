#!/bin/bash -eux

# Install Ansible repository.
apt-get -y update && apt-get -y upgrade
apt-get -y install software-properties-common
apt-add-repository ppa:ansible/ansible

# Install Ansible and Git.
apt-get -y update
apt-get -y install ansible git

cat > /tmp/requirements.yml << EOM
- name: ansible-role-packer-debian
  src: https://github.com/DevOps4Networks/ansible-role-packer-debian
- name: geerlingguy.nfs
EOM
sudo ansible-galaxy install --force -r /tmp/requirements.yml
