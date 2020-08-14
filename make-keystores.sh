#!/bin/bash

set -e

server_certificate=$1
ca_certificate=$2
store_password=$3
certificate_password=$4

if [ "$store_password" = "" ]
then
    echo 1>&2 "$0: missing argument(s)"
    echo 1>&2 "usage: $0 <server-certificate> <ca-certificate> <store-password> [ <certificate-password> ]"
fi

if ! [[ $server_certificate =~ \.p12$ ]]
then
    echo 1>&2 "$0: expected server_certificate argument to have a .p12 file extension"
    exit 1
fi

if ! [[ $ca_certificate =~ \.crt$ ]]
then
   echo 1>&2 "$0: expected ca_certificate to have a .crt extension"
   exit 1
fi

keytool -importkeystore \
        -srckeystore $server_certificate \
        -srcstorepass "$certificate_password" -srcstoretype PKCS12 \
        -deststorepass $store_password -destkeystore ${server_certificate%.p12}.ks \
        -deststoretype JKS -destkeypass $store_password \
        -noprompt 2>&1 | egrep -v '^(Warning:$|The JKS keystore uses a proprietary format.|$)'

keytool -import \
        -trustcacerts -alias $(basename $ca_certificate .crt) \
        -file $ca_certificate \
        -keystore ${ca_certificate%.crt}.ks -storetype JKS -deststorepass $store_password \
        -noprompt
