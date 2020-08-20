# Using nifi-toolkit to create SSL certificates

    ~/nifi-toolkit-1.11.4/bin/tls-toolkit.sh standalone -O -c <CA-HOSTNAME> -n <NIFI-HOSTNAME> -C 'CN=admin,OU=NiFi' -o certs

# Converting PKCS12 client certificate to PEM

    openssl pkcs12 -in <ADMIN-DN>.p12 -out CN=<ADMIN-DN>.pem -passin file:<ADMIN-DN>.password -nodes
