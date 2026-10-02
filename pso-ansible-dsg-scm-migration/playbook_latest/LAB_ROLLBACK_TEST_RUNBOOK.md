# Lab Rollback Test Runbook — rollback_firewall_to_panorama.yml

Target lab firewall: **dicks-vmseries-lab22-firewall01** (mgmt IP 40.76.96.112)
On-prem Panorama (from inventory `panorama` group): **13.72.98.89**
Backup consumed by Stage 1: `playbook_latest/firewalls_backups/running-config-dicks-vmseries-lab22-firewall01.xml`

> Run all commands from the repo root (where `ansible.cfg` / `inventory.yml` live),
> with your venv active and `--vault-password-file .vault_pass`.

---

## 0. Pre-flight (READ-ONLY — does NOT change or reboot the firewall)

Run these first so a real attempt isn't wasted on a bad credential / unreachable host / missing file.

### 0a. Inventory + vault sanity
```bash
ansible-inventory --graph
ansible-vault view group_vars/firewalls/credentials.yml --vault-password-file .vault_pass >/dev/null && echo "VAULT OK"
```

### 0b. Firewall reachable + API key works (read-only op)
```bash
ansible-playbook playbook_latest/reenable_panorama_management.yml \
  --vault-password-file .vault_pass \
  --limit dicks-vmseries-lab22-firewall01 \
  --tags NONEXISTENT_TAG_DRYCHECK --list-tasks
```
(That just lists tasks / confirms the play parses and the host resolves. It runs nothing.)

To actually confirm API connectivity without changing config, run a one-off op:
```bash
ansible dicks-vmseries-lab22-firewall01 -m paloaltonetworks.panos.panos_op \
  -a "cmd='show system info' provider='{\"ip_address\":\"40.76.96.112\"}'" \
  --vault-password-file .vault_pass -e @group_vars/firewalls/credentials.yml
```
Expect PAN-OS system info XML. If this fails, fix creds/connectivity BEFORE any staged run.

### 0c. Confirm the Stage-1 backup is what you expect
```bash
f=playbook_latest/firewalls_backups/running-config-dicks-vmseries-lab22-firewall01.xml
grep -n "cloud-service\|advance-routing\|panorama-server" "$f"
```
- **cloud-service present + advance-routing=yes** ⇒ this is a POST-migration capture
  (see runbook notes). End-to-end will still work via Stage 2/3 cleanup but adds a reboot.
- For a TRUE pre-migration test, replace this file with a clean baseline first.

---

## Option A — End-to-end (single run, ~2 reboots, ~25–35 min)

Use when you want one shot at the whole chain. Skips the optional SCM unclaim.

```bash
ansible-playbook playbook_latest/rollback_firewall_to_panorama.yml \
  --vault-password-file .vault_pass \
  --limit dicks-vmseries-lab22-firewall01,localhost \
  --skip-tags unclaim
```

**Success looks like:**
- Stage 1: "Pre-Migration Config Restore Complete", firewall REACHABLE after reboot.
- Stage 2: either "already disabled, no action needed" OR disable+reboot then "Advanced routing (after): DISABLED".
- Stage 3: "Panorama server set : SUCCESS", "Template push: ENABLED", "Shared-policy push: ENABLED".
  **← This is the task that failed for the client. If it says SUCCESS, the fix is proven.**

If it fails at **"Override-set <panorama-server>"**, apply the patch in the last section and re-run just Stage 3 (Option B, step 3).

---

## Option B — Staged (recommended when test attempts are scarce)

Each stage is independent and idempotent, so you can stop/inspect between them and
re-run a single stage without redoing the whole chain.

```bash
# Stage 1 — restore config + reboot
ansible-playbook playbook_latest/rollback_firewall_to_panorama.yml \
  --vault-password-file .vault_pass --limit dicks-vmseries-lab22-firewall01,localhost \
  --tags import_config

# Stage 2 — disable advanced routing (no-op if already off)
ansible-playbook playbook_latest/rollback_firewall_to_panorama.yml \
  --vault-password-file .vault_pass --limit dicks-vmseries-lab22-firewall01 \
  --tags disable_routing

# Stage 3 — reenable Panorama  ← the one that was failing
ansible-playbook playbook_latest/rollback_firewall_to_panorama.yml \
  --vault-password-file .vault_pass --limit dicks-vmseries-lab22-firewall01 \
  --tags reenable_panorama

# Stage 4 — unclaim from SCM (OPTIONAL)
ansible-playbook playbook_latest/rollback_firewall_to_panorama.yml \
  --vault-password-file .vault_pass --limit dicks-vmseries-lab22-firewall01,localhost \
  --tags unclaim
```

**Fastest way to prove the specific fix** (if the firewall is already in an SCM/migrated
state) is to run **Stage 3 only** — that directly re-creates the failure scenario and
proves the `override` works, in ~2–3 min with no reboot.

---

## Post-test verification (read-only)

```bash
ansible dicks-vmseries-lab22-firewall01 -m paloaltonetworks.panos.panos_op \
  -a "cmd='show system info' provider='{\"ip_address\":\"40.76.96.112\"}'" \
  --vault-password-file .vault_pass -e @group_vars/firewalls/credentials.yml
```
On the firewall GUI/CLI confirm:
- Device > Setup > Management > Panorama Settings → Panorama server = 13.72.98.89, no Cloud (SCM).
- `show system state | match advance-routing` → `advance-routing-enabled: False`.
- Panorama shows the device connected again.

---

## READY PATCH — only if Stage 3 fails at "Override-set <panorama-server>"

Current code uses set-style xpath. If the lab errors on that task, switch to edit-style
(xpath points at the node itself). In `reenable_panorama_management.yml`, task
**"Override-set <panorama-server> to on-prem Panorama IP"**, change the `uri` body:

```yaml
# BEFORE (set-style)
      xpath: "/config/devices/entry[@name='localhost.localdomain']/deviceconfig/system"
      element: "<panorama-server>{{ effective_panorama_server }}</panorama-server>"

# AFTER (edit-style — xpath includes /panorama-server)
      xpath: "/config/devices/entry[@name='localhost.localdomain']/deviceconfig/system/panorama-server"
      element: "<panorama-server>{{ effective_panorama_server }}</panorama-server>"
```

Then re-run Stage 3 only (Option B, step 3). No reboot needed.
```

Rollback tip: if a lab run leaves the firewall half-migrated, just re-run the failed
stage — every stage is idempotent by design.
