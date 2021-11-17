#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: nso_rollback
extends_documentation_fragment:
- cisco.nso.nso
'''

EXAMPLES = '''
- name: ROLLBACK to specific id
  cisco.nso.nso_rollback:
    url: https://10.10.20.49/jsonrpc
    username: developer
    password: C1sco12345
'''

RETURN = '''
changes:
    description: List of changes
    returned: always
    type: complex
    sample:
        - path: "/ncs:devices/device{dist-rtr01}/config/ios:interface/Loopback{1}/ip/address/primary/address"
          from: null
          to: "10.10.10.10"
          type: set
    contains:
        path:
            description: Path to value changed
            returned: always
            type: str
        from:
            description: Previous value if any, else null
            returned: When previous value is present on value change
            type: str
'''

from ansible_collections.cisco.nso.plugins.module_utils.nso import connect, verify_version, nso_argument_spec
from ansible_collections.cisco.nso.plugins.module_utils.nso import ModuleFailException, NsoException
from ansible.module_utils.basic import AnsibleModule


class NsoRollback(object):
    REQUIRED_VERSIONS = [
        (5, 1)
    ]

    def __init__(self, check_mode, client, data):
        self._check_mode = check_mode
        self._client = client
        self._data = data

        self._changes = []
        self._diffs = []
        self._commit_result = []

    def main(self):
        # Figure out what to do
        #
        # Call self._get_rollbacks() to translate commit id to index

        # self._changes should likely be derived from get_trans_changes RPC for load_rollback
        #   otherwise empty
        # self._commit_result should be available from any of the actions
        # self._diffs doesn't really make sense here...?
        return self._changes, self._diffs, self._commit_result

    def _get_rollbacks(self):
        self._commit_result = self._client.get_rollbacks()

        # result is a list of rollback entries:
        #
        # rollback = {
        #   nr:             0-based from most current commit going backwards
        #   filename:       string
        #   creator:        string
        #   date:           string
        #   via:            string [cli, system, netconf, webui]
        #   label:          string
        #   comment:        string
        #   rollback_nr:    commit id
        # }


def main():
    argument_spec = dict(
        id=dict(required=False, type='number'),
    )

    argument_spec.update(nso_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )
    p = module.params
    client = connect(p)
    nso_rollback = NsoRollback(module.check_mode, client, p['data'])
    try:
        verify_version(client, NsoRollback.REQUIRED_VERSIONS)

        changes, diffs, commit_result = nso_rollback.main()
        client.logout()

        changed = len(changes) > 0
        module.exit_json(
            changed=changed, changes=changes, diffs=diffs, commit_result=commit_result)

    except NsoException as ex:
        client.logout()
        module.fail_json(msg=ex.message)
    except ModuleFailException as ex:
        client.logout()
        module.fail_json(msg=ex.message)


if __name__ == '__main__':
    main()
