#!/bin/sh

# Set a domain name in Route53.  The complete domain name and the IPv4
# address to associate with it need to be specified on the command
# line.  AWS CLI needs to be configured so that the proper access key
# is used, e.g. by the way of the default configuration, by setting
# the AWS_PROFILE environment variable or by some other, equivalent
# means
# (https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html).

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
