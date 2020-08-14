#!/bin/sh

set -e

name=$1
ssh_key=$2

ip_address=$(./make-hetzner-vm.sh $name $ssh_key)

until nc $ip_address 22 < /dev/null
do
    echo waiting for virtual machine to come up
    sleep 3
done

ansible-playbook -i $ip_address, bootstrap.yaml
