#!/bin/sh

set -e

DNSNAME=$1
ADDRESS=$2

if [ "$ADDRESS" = "" ]
then
    echo 1>&2 "usage: $0 <dns-name> <ip-address>"
    exit 1
fi

DOMAIN=$(echo $DNSNAME | sed -e 's/.*\.\([^.]*\.[^.]*\)$/\1/')
ZONE_ID=$(aws --query 'HostedZones[0].Id' --output text \
              route53 list-hosted-zones-by-name --dns-name $DOMAIN)
CHANGE_ID=$(aws --query 'ChangeInfo.Id' --output text \
                route53 change-resource-record-sets \
                --hosted-zone $ZONE_ID --change-batch '
{"Changes":[{"Action":"UPSERT",
             "ResourceRecordSet":{
                "ResourceRecords":[{"Value":"'$ADDRESS'"}],
                        "Name": "'$DNSNAME'",
                        "Type": "A",
                        "TTL": 30
                }}]}')
echo 1>&2 $0: set A record for $DNSNAME to $ADDRESS, waiting for change to propagate
while [ $(aws --query 'ChangeInfo.Status' --output text route53 get-change --id $CHANGE_ID) != INSYNC ]
do
    sleep 2
done
echo 1>&2 $0: the A record has been propagated to the Route53 servers
