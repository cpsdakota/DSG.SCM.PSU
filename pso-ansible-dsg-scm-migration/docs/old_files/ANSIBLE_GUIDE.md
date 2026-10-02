# Ansible Integration Guide for SCM Device Registration

This guide explains how to automate the Palo Alto NGFW device registration process in Strata Cloud Manager (SCM) using Ansible.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Authentication Setup](#authentication-setup)
- [Ansible Inventory](#ansible-inventory)
- [Playbook Examples](#playbook-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The SCM device registration process can be automated using Ansible by leveraging the `uri` module to interact with the SCM REST APIs. This guide provides playbooks for:

- Listing registered devices
- Retrieving available label groups
- Claiming/registering devices to SCM
- Bulk device registration operations

## Prerequisites

### Required Software

- Ansible 2.9 or higher
- Python 3.10+ (on the Ansible control node)
- `ansible-vault` for secure credential storage

### SCM Credentials

You'll need the following credentials from your Palo Alto Strata Cloud Manager:

- **Client ID**: Service account client ID (format: `xxx@yyy.iam.panserviceaccount.com`)
- **Client Secret**: Service account client secret
- **TSG ID**: Tenant Service Group ID

### API Endpoints

The playbooks use these SCM API endpoints:

- **Auth**: `https://auth.apps.paloaltonetworks.com/oauth2/access_token`
- **List Devices**: `https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices`
- **Label Groups**: `https://paas-11.prod.panorama.paloaltonetworks.com/api/sase/config/v1/device-config/label-groups`
- **Claim Devices**: `https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim`

## Authentication Setup

### Using Ansible Vault (Recommended)

1. Create an encrypted variables file:

```bash
ansible-vault create group_vars/all/scm_credentials.yml
```

2. Add your SCM credentials:

```yaml
---
scm_client_id: "your-client-id@tenant.iam.panserviceaccount.com"
scm_client_secret: "your-client-secret"
scm_tsg_id: "your-tenant-service-group-id"
```

3. Save and exit. You'll be prompted to create a vault password.

4. Store the vault password securely:

```bash
# Option 1: Use a password file
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore
echo ".vault_pass" >> .gitignore
```

### Alternative: Environment Variables

You can also use environment variables (less secure for production):

```bash
export SCM_CLIENT_ID="your-client-id@tenant.iam.panserviceaccount.com"
export SCM_CLIENT_SECRET="your-client-secret"
export SCM_TSG_ID="your-tenant-service-group-id"
```

Then reference them in your playbook:

```yaml
vars:
  scm_client_id: "{{ lookup('env', 'SCM_CLIENT_ID') }}"
  scm_client_secret: "{{ lookup('env', 'SCM_CLIENT_SECRET') }}"
  scm_tsg_id: "{{ lookup('env', 'SCM_TSG_ID') }}"
```

## Ansible Inventory

Create an inventory file for your NGFW devices:

### inventory/hosts.yml

```yaml
all:
  children:
    palo_alto_firewalls:
      hosts:
        pa-vm-001:
          serial_number: "007958000744783"
          device_labels: []
        pa-vm-002:
          serial_number: "007958000744784"
          device_labels: ["production", "datacenter-1"]
        pa-vm-003:
          serial_number: "007958000744785"
          device_labels: ["staging"]
      vars:
        scm_device_type: "registered"
```

## Playbook Examples

### 1. Get OAuth2 Token

Create a reusable role or task file for authentication:

**roles/scm_auth/tasks/main.yml**

```yaml
---
- name: Obtain SCM OAuth2 token
  uri:
    url: "https://auth.apps.paloaltonetworks.com/oauth2/access_token"
    method: POST
    body_format: form-urlencoded
    body:
      client_id: "{{ scm_client_id }}"
      client_secret: "{{ scm_client_secret }}"
      grant_type: "client_credentials"
      scope: "tsg_id:{{ scm_tsg_id }}"
    status_code: 200
    return_content: yes
  register: scm_token_response
  no_log: true  # Don't log sensitive token data

- name: Set token facts
  set_fact:
    scm_access_token: "{{ scm_token_response.json.access_token }}"
    scm_token_expires_in: "{{ scm_token_response.json.expires_in }}"
  no_log: true
```

### 2. List Registered Devices

**playbooks/list_devices.yml**

```yaml
---
- name: List SCM registered devices
  hosts: localhost
  gather_facts: no
  vars_files:
    - ../group_vars/all/scm_credentials.yml

  tasks:
    - name: Authenticate with SCM
      include_role:
        name: scm_auth

    - name: List registered devices
      uri:
        url: "https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices"
        method: GET
        headers:
          x-auth-jwt: "{{ scm_access_token }}"
          Content-Type: "application/json"
        body_format: json
        status_code: [200, 201]
        return_content: yes
      register: devices_response

    - name: Display devices
      debug:
        msg: "{{ devices_response.json }}"

    - name: Show device summary
      debug:
        msg: "Serial: {{ item.id }} | Model: {{ item.model }} | Status: {{ item.status }}"
      loop: "{{ devices_response.json }}"
      when: devices_response.json is iterable
```

Run with:

```bash
ansible-playbook playbooks/list_devices.yml --vault-password-file .vault_pass
```

### 3. Retrieve Label Groups

**playbooks/get_label_groups.yml**

```yaml
---
- name: Get SCM label groups
  hosts: localhost
  gather_facts: no
  vars_files:
    - ../group_vars/all/scm_credentials.yml

  tasks:
    - name: Authenticate with SCM
      include_role:
        name: scm_auth

    - name: Get label groups
      uri:
        url: "https://paas-11.prod.panorama.paloaltonetworks.com/api/sase/config/v1/device-config/label-groups"
        method: GET
        headers:
          x-auth-jwt: "{{ scm_access_token }}"
          Content-Type: "application/json"
        body_format: json
        status_code: 200
        return_content: yes
      register: labels_response

    - name: Display available labels
      debug:
        msg: "ID: {{ item.id }} | Name: {{ item.name }} | Description: {{ item.description | default('N/A') }}"
      loop: "{{ labels_response.json.data }}"
      when: labels_response.json.data is defined
```

### 4. Claim Single Device

**playbooks/claim_device.yml**

```yaml
---
- name: Claim NGFW device to SCM
  hosts: localhost
  gather_facts: no
  vars_files:
    - ../group_vars/all/scm_credentials.yml
  vars:
    device_serial: "007958000744783"
    device_labels: []  # Optional: Add label IDs here

  tasks:
    - name: Authenticate with SCM
      include_role:
        name: scm_auth

    - name: Claim device to SCM
      uri:
        url: "https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim"
        method: POST
        headers:
          x-auth-jwt: "{{ scm_access_token }}"
          Content-Type: "application/json"
        body_format: json
        body:
          devices:
            - "{{ device_serial }}"
          labels: "{{ device_labels }}"
        status_code: 200
        return_content: yes
      register: claim_response

    - name: Display claim result
      debug:
        var: claim_response.json

    - name: Check claim status
      debug:
        msg: "Task {{ claim_response.json.task_id }}: {{ claim_response.json.status }}"
      when: claim_response.json.task_id is defined
```

Run with:

```bash
ansible-playbook playbooks/claim_device.yml \
  --vault-password-file .vault_pass \
  -e "device_serial=007958000744783"
```

### 5. Bulk Device Registration

**playbooks/bulk_claim_devices.yml**

```yaml
---
- name: Bulk claim NGFW devices to SCM
  hosts: localhost
  gather_facts: no
  vars_files:
    - ../group_vars/all/scm_credentials.yml

  tasks:
    - name: Authenticate with SCM
      include_role:
        name: scm_auth

    - name: Build device list from inventory
      set_fact:
        device_serials: "{{ groups['palo_alto_firewalls'] | map('extract', hostvars, 'serial_number') | list }}"

    - name: Display devices to be claimed
      debug:
        msg: "Will claim {{ device_serials | length }} devices: {{ device_serials }}"

    - name: Claim all devices
      uri:
        url: "https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim"
        method: POST
        headers:
          x-auth-jwt: "{{ scm_access_token }}"
          Content-Type: "application/json"
        body_format: json
        body:
          devices: "{{ device_serials }}"
          labels: []
        status_code: 200
        return_content: yes
      register: bulk_claim_response

    - name: Display bulk claim results
      debug:
        msg: "Device {{ item.serial_number }}: {{ item.association_status }}"
      loop: "{{ bulk_claim_response.json.devices }}"
      when: bulk_claim_response.json.devices is defined
```

### 6. Claim Devices with Labels

**playbooks/claim_with_labels.yml**

```yaml
---
- name: Claim devices with label assignment
  hosts: palo_alto_firewalls
  gather_facts: no
  vars_files:
    - ../group_vars/all/scm_credentials.yml
  serial: 1  # Process devices one at a time

  tasks:
    - name: Authenticate with SCM
      include_role:
        name: scm_auth
      delegate_to: localhost
      run_once: true

    - name: Claim device with labels
      uri:
        url: "https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim"
        method: POST
        headers:
          x-auth-jwt: "{{ hostvars['localhost']['scm_access_token'] }}"
          Content-Type: "application/json"
        body_format: json
        body:
          devices:
            - "{{ serial_number }}"
          labels: "{{ device_labels | default([]) }}"
        status_code: 200
        return_content: yes
      delegate_to: localhost
      register: claim_response

    - name: Report claim status
      debug:
        msg: "{{ inventory_hostname }} ({{ serial_number }}): {{ claim_response.json.status }}"
```

## Best Practices

### 1. Token Management

- **Token Caching**: Store tokens in facts and reuse them across tasks
- **Expiration Handling**: Check token expiry (default 3600s) and refresh when needed
- **Security**: Always use `no_log: true` for tasks handling tokens

```yaml
- name: Check if token needs refresh
  set_fact:
    token_needs_refresh: "{{ (ansible_date_time.epoch | int) > (scm_token_obtained_at | default(0) | int + scm_token_expires_in | default(0) | int - 60) }}"

- name: Refresh token if needed
  include_role:
    name: scm_auth
  when: token_needs_refresh | default(true) | bool
```

### 2. Error Handling

```yaml
- name: Claim device with error handling
  block:
    - name: Attempt to claim device
      uri:
        url: "https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim"
        method: POST
        headers:
          x-auth-jwt: "{{ scm_access_token }}"
        body_format: json
        body:
          devices: ["{{ device_serial }}"]
          labels: []
        status_code: 200
      register: claim_result

  rescue:
    - name: Handle claim failure
      debug:
        msg: "Failed to claim device {{ device_serial }}: {{ claim_result.msg | default('Unknown error') }}"

    - name: Log error details
      debug:
        var: claim_result
      when: ansible_verbosity >= 1

  always:
    - name: Record attempt
      set_fact:
        claim_attempted: true
```

### 3. Idempotency

```yaml
- name: Check if device is already registered
  uri:
    url: "https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices"
    method: GET
    headers:
      x-auth-jwt: "{{ scm_access_token }}"
    status_code: [200, 201]
  register: existing_devices

- name: Filter already registered devices
  set_fact:
    already_registered: "{{ existing_devices.json | map(attribute='id') | list }}"

- name: Claim only unregistered devices
  uri:
    url: "https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim"
    method: POST
    headers:
      x-auth-jwt: "{{ scm_access_token }}"
    body_format: json
    body:
      devices: "{{ device_serials | difference(already_registered) }}"
      labels: []
  when: (device_serials | difference(already_registered)) | length > 0
```

### 4. Logging and Reporting

```yaml
- name: Create results directory
  file:
    path: "./claim_results"
    state: directory
  delegate_to: localhost
  run_once: true

- name: Save claim results
  copy:
    content: "{{ claim_response.json | to_nice_json }}"
    dest: "./claim_results/claim_{{ ansible_date_time.iso8601_basic_short }}.json"
  delegate_to: localhost
```

### 5. Parallel Execution

For better performance when claiming multiple devices:

```yaml
- name: Bulk claim in parallel (with strategy)
  hosts: palo_alto_firewalls
  strategy: free  # Allow parallel execution
  gather_facts: no
  # ... rest of playbook
```

## Directory Structure

Recommended Ansible project structure:

```
scm-device-automation/
├── ansible.cfg
├── inventory/
│   ├── production/
│   │   └── hosts.yml
│   └── staging/
│       └── hosts.yml
├── group_vars/
│   └── all/
│       └── scm_credentials.yml  # Vault encrypted
├── roles/
│   └── scm_auth/
│       └── tasks/
│           └── main.yml
├── playbooks/
│   ├── list_devices.yml
│   ├── get_label_groups.yml
│   ├── claim_device.yml
│   ├── bulk_claim_devices.yml
│   └── claim_with_labels.yml
└── .vault_pass  # Gitignored
```

### Sample ansible.cfg

```ini
[defaults]
inventory = inventory/production
vault_password_file = .vault_pass
host_key_checking = False
retry_files_enabled = False
gathering = explicit

[privilege_escalation]
become = False
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Symptom**: 401 Unauthorized errors

**Solution**:
```yaml
- name: Debug authentication
  debug:
    msg:
      - "Client ID: {{ scm_client_id }}"
      - "TSG ID: {{ scm_tsg_id }}"
      - "Token present: {{ scm_access_token is defined }}"
```

#### 2. Token Expiration

**Symptom**: Requests fail midway through playbook

**Solution**: Implement token refresh logic (see Best Practices)

#### 3. Invalid Serial Numbers

**Symptom**: Device claim fails with error

**Solution**:
```yaml
- name: Validate serial number format
  assert:
    that:
      - device_serial is defined
      - device_serial | length > 0
    fail_msg: "Invalid or missing device serial number"
```

### Verbose Mode

Run playbooks with verbose output for debugging:

```bash
# Show task results
ansible-playbook playbooks/claim_device.yml -v

# Show detailed connection info
ansible-playbook playbooks/claim_device.yml -vv

# Show full debug output
ansible-playbook playbooks/claim_device.yml -vvv
```

### Testing API Endpoints

Use the `uri` module with `check_mode` for testing:

```yaml
- name: Test API connectivity
  uri:
    url: "https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices"
    method: GET
    headers:
      x-auth-jwt: "{{ scm_access_token }}"
    validate_certs: yes
    return_content: yes
  check_mode: yes
  register: api_test
```

## Advanced Scenarios

### Dynamic Inventory from SCM

Create a dynamic inventory script that fetches devices from SCM:

**inventory/scm_inventory.py**

```python
#!/usr/bin/env python3
import json
import requests
import os

def get_scm_token():
    response = requests.post(
        "https://auth.apps.paloaltonetworks.com/oauth2/access_token",
        data={
            "client_id": os.environ["SCM_CLIENT_ID"],
            "client_secret": os.environ["SCM_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": f"tsg_id:{os.environ['SCM_TSG_ID']}"
        }
    )
    return response.json()["access_token"]

def get_devices(token):
    response = requests.get(
        "https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices",
        headers={"x-auth-jwt": token},
        params={"type": "registered"}
    )
    return response.json()

if __name__ == "__main__":
    token = get_scm_token()
    devices = get_devices(token)

    inventory = {
        "_meta": {"hostvars": {}},
        "scm_devices": {"hosts": []}
    }

    for device in devices:
        hostname = f"pa-{device['id']}"
        inventory["scm_devices"]["hosts"].append(hostname)
        inventory["_meta"]["hostvars"][hostname] = {
            "serial_number": device["id"],
            "model": device.get("model"),
            "status": device.get("status")
        }

    print(json.dumps(inventory, indent=2))
```

Make it executable and use it:

```bash
chmod +x inventory/scm_inventory.py
ansible-playbook playbooks/some_playbook.yml -i inventory/scm_inventory.py
```

## References

- [Ansible URI Module Documentation](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html)
- [Ansible Vault Guide](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [Palo Alto Networks SCM API Documentation](https://docs.paloaltonetworks.com/)

## Contributing

When adding new playbooks or roles:

1. Follow the directory structure above
2. Use Ansible Vault for all credentials
3. Include error handling in all tasks
4. Add comments explaining complex logic
5. Test playbooks in staging before production
6. Document any new variables or dependencies

---

**Note**: This guide assumes you have basic familiarity with Ansible. For Ansible basics, refer to the [official Ansible documentation](https://docs.ansible.com/).
