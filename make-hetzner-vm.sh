#!/bin/sh

set -e

name=$1
ssh_key=$2

echo 1>&2 creating virtual machine instance

hcloud server create --type cx31 \
       --location fsn1 \
       --image ubuntu-20.04 \
       --name=$name \
       --ssh-key $ssh_key 1>&2

hcloud server describe --output json $name \
    | jq -r .public_net.ipv4.ip
