# Ansible Playbook to deploy Apache NiFi

This Ansible playbook installs, configures and deploys Apache NiFi on
a (virtual) machine that is assumed to be dedicated for this purpose.
It performs the required system tuning steps, network configuration,
prerequisite installation and initial flow configuration of Apache
NiFi.  It also installs the Apache NiFi Registry and connects it to a
GitHub repository for flow configuration storage.

Even though the intent is to completely automate the process, there
are a few steps that need to be executed in sequence to set up a NiFi
instance as each of the steps can be varied according to the needs of
the environment being set up.  The steps are:

 1. Set up a (virtual) machine
 2. Register the IPv4 address in the DNS
 3. Create a TLS certificate
 4. Configure environment
 5. Deploy NiFi and its dependencies
 
The results of the preparatory steps are all stored in a YAML
inventory file that is then used by Ansible to run the main playbook.
Each of the steps is described below.

## Set up a (virtual) machine

Included in this repository is the script `make-hetzner-vm.sh` which
creates a suitable virtual machine in the Hetzner cloud.  It uses the
[hcloud](https://github.com/hetznercloud/cli) command line utility,
which needs to be installed locally and configured with the desired
access token before the script is run as follows:

    ./make-hetzner-vm.sh <name> <ssh-key>

The `<name>` is used to identify the virtual machine on Hetzner's
side.  It can be the same as the host name that is being used for the
NiFi instance.  `<ssh-key>` indicates the name of the ssh key that
should have access to the `root` account on the new virtual machine.
The key needs to be registered with Hetzner beforehand, using the web
interface or `hcloud`.  This key must be present on the machine and to
the user that is used to run Ansible later on.

The script prints the IPv4 address of the new virtual machine on the
standard output when it finishes.

It is possible to provision the virtual machine using any other means,
as long as ssh access to the root account is provided for the initial
Ansible setup.

## Register the IPv4 address in the DNS

In order for the NiFi instance to be usable, a DNS domain name must be
registered for it.  If AWS Route53 is used as DNS provider for the
zone in which the name resides, the `set-dns-name-route53.sh` script
can be used to associate the DNS name with the IPv4 address of the
NiFi instance like so:

    ./set-dns-name-route53.sh <name> <address>
    
`<name>` is the fully qualified domain name to register, `<address>`
is the IPv4 address of the NiFi instance as determined previously.

In order to use this script, the [AWS CLI](https://aws.amazon.com/cli)
needs to be installed locally and configured with an appropriate
access token.  The AWS CLI is available in most operating system
package repositories.

## Create a TLS certificate

## Configure environment

Additional configuration parameters can be set in the inventory for
the new virtual machine:

### Logging

The
[logstash](https://www.elastic.co/guide/en/logstash/current/introduction.html)
data collection engine is deployed on the Ansible host to centralize
and streamline the collection and distribution of logging
information.  It is configured to collect the system and application
logs and send it to a downstream logging system.

#### Logging to Elasticsearch

In order to log to an Elasticsearch instance, the following parameters
need to be set in the inventory:

    logstash_elasticsearch_hosts:
      - <elasticsearch-url>
    logstash_elasticsearch_index: <index-name>
    
`<elasticsearch-url>` is the url of Elasticsearch that logs need to be
written to.  If basic authentication needs to be used, the username
and password need to be included in the url
(`https://<user>:<password>@<host>:<port>/...`).  The `<index-name>`
determines the index into which logs are written,
e.g. `"nifi_dev-%{+YYYY.MM.dd}"`.

#### Logging to DataDog

Logs can be sent to DataDog by setting the following parameter:

    logstash_datadog_log_api_key: <api-key>
    
`<api-key>` needs to be a valid API key for the account.  By default,
logs are sent to Datadog's European log ingestion endpoint
(`http-intake.logs.datadoghq.eu`).  This can be overridden by setting
the configuration parameter `logstash_datadog_log_host` to the
appropriate host name in the inventory.

## Deploy NiFi and its dependencies

With all parameters present in the Inventory file, Ansible can be run
to install and configure NiFi and its dependencies on the virtual
machine.

# Miscelleneous notes

## Using nifi-toolkit to create SSL certificates

    ~/nifi-toolkit-1.11.4/bin/tls-toolkit.sh standalone -O -c <CA-HOSTNAME> -n <NIFI-HOSTNAME> -C 'CN=admin,OU=NiFi' -o certs

## Converting PKCS12 client certificate to PEM

    openssl pkcs12 -in <ADMIN-DN>.p12 -out CN=<ADMIN-DN>.pem -passin file:<ADMIN-DN>.password -nodes
