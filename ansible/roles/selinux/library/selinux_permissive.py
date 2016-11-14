#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Michael Scherer <misc@zarb.org>
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

import sys
# import module snippets
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: selinux_permissive
short_description: Change permissive domain in SELinux policy
description:
  - Add and remove domain from the list of permissive domain.
version_added: "1.8"
options:
  domain:
    description:
        - "the domain that will be added or removed from the list of permissive domains"
    required: true
  permissive:
    description:
        - "indicate if the domain should or should not be set as permissive"
    required: true
  no_reload:
    description:
        - "automatically reload the policy after a change"
        - "default is 'true' as that's what most people would want after changing one domain"
        - "Note that this doesn't work on older version of the library (example EL 6),
        the module will silently ignore it in this case"
    required: false
    default: False
  store:
    description:
      - "name of the SELinux policy store to use"
    required: false
    default: null
notes:
    - Requires a version of SELinux recent enough ( ie EL 6 or newer )
requirements: [ policycoreutils-python ]
author: Michael Scherer <misc@zarb.org>
'''

EXAMPLES = '''
- selinux_permissive: name=httpd_t permissive=true
'''
try:
    import seobject
except ImportError:
    seobject = None
    print("failed=True msg='policycoreutils-python required for this module'")
    sys.exit(1)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(aliases=['name'], required=True),
            store=dict(required=False, default=''),
            permissive=dict(type='bool', required=True),
            no_reload=dict(type='bool', required=False, default=False),
        ),
        supports_check_mode=False
    )

    # global vars
    changed = False
    store = module.params['store']
    permissive = module.params['permissive']
    domain = module.params['domain']
    no_reload = module.params['no_reload']

    try:
        permissive_domains = seobject.permissiveRecords(store)
    except ValueError as e:
        module.fail_json(domain=domain, msg=str(e))
        raise AssertionError

    # not supported on EL 6
    if 'set_reload' in dir(permissive_domains):
        permissive_domains.set_reload(not no_reload)

    if permissive:
        if domain not in permissive_domains.get_all():
            changed = True
            permissive_domains.add(domain)
    else:
        if domain in permissive_domains.get_all():
            changed = True
            permissive_domains.delete(domain)

    module.exit_json(changed=changed, store=store,
                     permissive=permissive, domain=domain)


#################################################
if __name__ == '__main__':
    main()
