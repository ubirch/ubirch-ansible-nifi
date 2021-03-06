#!/usr/bin/env python3

import sys

from uuid import uuid4
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

initial_administrator = sys.argv[1]
additional_administrators = sys.argv[2].split(',')

policies=[
    { 'resource': '/flow', 'action': 'R' },
    { 'resource': '/restricted-components', 'action': 'W' },
    { 'resource': '/tenants', 'action': 'R' },
    { 'resource': '/tenants', 'action': 'W' },
    { 'resource': '/policies', 'action': 'R' },
    { 'resource': '/policies', 'action': 'W' },
    { 'resource': '/controller', 'action': 'R' },
    { 'resource': '/controller', 'action': 'W' },
    { 'resource': '/counters', 'action': 'R' }]

root_group_policies=[
    { 'resource': '/data/process-groups/', 'action': 'R' },
    { 'resource': '/data/process-groups/', 'action': 'W' },
    { 'resource': '/process-groups/', 'action': 'R' },
    { 'resource': '/process-groups/', 'action': 'W' },
    { 'resource': '/operation/process-groups/', 'action': 'W' },
    { 'resource': '/provenance-data/process-groups/', 'action': 'R' }]

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

administrators = list(map(lambda identity: { 'identity': identity, 'identifier': str(uuid4()) },
                          [ initial_administrator ] + additional_administrators))

admin_group_id = str(uuid4())
root_group_id = str(uuid4())

## Create flow.xml

flowControllerElement = Element('flowController', { 'encoding-version': '1.4' });
SubElement(flowControllerElement, 'maxTimerDrivenThreadCount').text = '10'
SubElement(flowControllerElement, 'maxEventDrivenThreadCount').text = '1'
registriesElement = SubElement(flowControllerElement, 'registries')
flowRegistryElement = SubElement(registriesElement, 'flowRegistry')
SubElement(flowRegistryElement, 'id').text = str(uuid4())
SubElement(flowRegistryElement, 'name').text = 'localhost'
SubElement(flowRegistryElement, 'url').text = 'http://localhost:18080'
SubElement(flowRegistryElement, 'description')
SubElement(flowControllerElement, 'parameterContexts')
rootGroupElement = SubElement(flowControllerElement, 'rootGroup')
SubElement(rootGroupElement, 'id').text = root_group_id
SubElement(rootGroupElement, 'name').text = 'NiFi Flow'
SubElement(rootGroupElement, 'position', { 'x': '0.0', 'y': '0.0' })
SubElement(rootGroupElement, 'comment')
SubElement(flowControllerElement, 'controllerServices')
SubElement(flowControllerElement, 'reportingTasks')

with open('flow.xml', 'w', encoding='utf-8') as outfile:
    outfile.write(prettify(flowControllerElement))

## Create users.xml

tenants_element = Element('tenants')

groups = SubElement(tenants_element, 'groups')
admin_group_element = SubElement(groups,
                                 'group',
                                 { 'name': 'Administrators',
                                   'identifier': admin_group_id })
for administrator in administrators:
    SubElement(admin_group_element, 'user', { 'identifier': administrator['identifier'] })

users_element = SubElement(tenants_element, 'users')
for administrator in administrators:
    SubElement(users_element, 'user', administrator)

with open('users.xml', 'w', encoding='utf-8') as outfile:
    outfile.write(prettify(tenants_element))

## Create authorizations.xml

authorizations_element = Element('authorizations')

policies_element = SubElement(authorizations_element, 'policies')
for policy in policies:
    policy = policy.copy()
    policy['identifier'] = str(uuid4())
    policy_element = SubElement(policies_element, 'policy', policy)
    SubElement(policy_element, 'group', { 'identifier': admin_group_id })
for policy in root_group_policies:
    policy = policy.copy()
    policy['identifier'] = str(uuid4())
    policy['resource'] = policy['resource'] + root_group_id
    policy_element = SubElement(policies_element, 'policy', policy)
    SubElement(policy_element, 'group', { 'identifier': admin_group_id })

with open('authorizations.xml', 'w', encoding='utf-8') as outfile:
    outfile.write(prettify(authorizations_element))
