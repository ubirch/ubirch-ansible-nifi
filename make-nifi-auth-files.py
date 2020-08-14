#!/usr/bin/env python3

import sys

root_group_id = sys.argv[1]
initial_administrator = sys.argv[2]
additional_administrators = sys.argv[3].split(',')

policies=[
    { 'resource': '/flow', 'action': 'R' },
    { 'resource': '/restricted-components', 'action': 'W' },
    { 'resource': '/tenants', 'action': 'R' },
    { 'resource': '/tenants', 'action': 'W' },
    { 'resource': '/policies', 'action': 'R' },
    { 'resource': '/policies', 'action': 'W' },
    { 'resource': '/controller', 'action': 'R' },
    { 'resource': '/controller', 'action': 'W' }]

root_group_policies=[
    { 'resource': '/data/process-groups/', 'action': 'R' },
    { 'resource': '/data/process-groups/', 'action': 'W' },
    { 'resource': '/process-groups/', 'action': 'R' },
    { 'resource': '/process-groups/', 'action': 'W' },
    { 'resource': '/operation/process-groups/', 'action': 'W' },
    { 'resource': '/provenance-data/process-groups/', 'action': 'R' }]

from uuid import uuid4
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

administrators = list(map(lambda identity: { 'identity': identity, 'identifier': str(uuid4()) },
                          [ initial_administrator ] + additional_administrators))

admin_group_id = str(uuid4())

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
authorizations_element.set('version', '1.0')

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

