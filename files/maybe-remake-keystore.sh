#!/bin/sh

set -e

HOSTNAME=$(hostname)
PASSWORD=$(perl -ne 'print "$1\n" if (/^nifi.security.keystorePasswd=(.*)/)' /opt/nifi/nifi-current/conf/nifi.properties)
CERTS_DIR=/etc/letsencrypt/live/$HOSTNAME

KEYSTORE=/opt/nifi/nifi-current/conf/keystore.ks
TMP_PKCS12=/tmp/$HOSTNAME.p12

if [ ! -f $KEYSTORE -o $CERTS_DIR/cert.pem -nt $KEYSTORE ]
then
    if systemctl is-active nifi
    then
        NIFI_ACTIVE=1
        systemctl stop nifi
    fi
    trap "rm -f $PCKS12" 0
    openssl pkcs12 \
            -export \
	    -in $CERTS_DIR/cert.pem \
	    -inkey $CERTS_DIR/privkey.pem \
	    -out $TMP_PKCS12 \
	    -name $HOSTNAME \
	    -CAfile $CERTS_DIR/fullchain.pem \
	    -caname "Let's Encrypt Authority X3" \
	    -password "pass:$PASSWORD"
    keytool -importkeystore \
	    -noprompt \
	    -deststorepass "$PASSWORD" \
	    -destkeypass "$PASSWORD" \
	    -deststoretype pkcs12 \
	    -srckeystore $TMP_PKCS12 \
	    -srcstoretype PKCS12 \
	    -srcstorepass "$PASSWORD" \
	    -destkeystore $KEYSTORE \
	    -alias $HOSTNAME
    if [ "$NIFI_ACTIVE" -ne "" ]
    then
        systemctl start nifi
    fi
fi
