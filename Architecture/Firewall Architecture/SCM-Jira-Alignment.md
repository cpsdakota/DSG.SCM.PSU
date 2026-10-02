# SCM Jira Alignment

## Purpose

Map the proposed SCM new-store firewall lifecycle directly to Jira workstreams so stakeholders can see how the implementation backlog supports the operating process.

This document is intentionally **process-first**. The lifecycle defines what must happen; Jira tracks the work required to make each phase reliable, repeatable, supportable, and eventually automated.

---
# 1\. Lifecycle to Jira Map

|Lifecycle Phase|Jira Workstream|Primary Outcome|
|-|-|-|
|1. Intake / Bootstrap|Firewall Intake \& Discovery|PA-440 reaches a known, reachable staging baseline|
|2. Discovery|Firewall Intake \& Discovery|Current firewall state is observed and normalized|
|3. Software / Content Preparation|Software \& Content Staging|PAN-OS and content are brought to approved levels|
|4. Advanced Routing|Advanced Routing Preparation|Advanced Routing is configured, activated, and verified|
|5. Cloud Management|Cloud Management Enablement|Firewall is placed into cloud-management mode and verified locally|
|6. SCM Onboarding|SCM Device Onboarding|Device is claimed, visible, and connected in SCM|
|7. Store Assignment|Store ↔ Serial Integration|Existing assignment workflows continue to feed the SCM build|
|8. Store Configuration|SCM Desired State / Snippets|Store-specific SCM configuration is created or reconciled|
|9. Push / Verification|SCM Push \& Effective-State Verification|Configuration is pushed and actual end state is proven|
|10. Deployment Ready|Reporting / Dashboard / Completion|Device is clearly marked ready for Store Projects / deployment|
|Cross-cutting|Manual Runbook|Supported manual process exists independently of orchestration|
|Cross-cutting|Dashboard 2.0|Operators can view state and perform approved one-off actions|
|Cross-cutting|Durable Workflow State / Audit History|Workflow progress, retries, locks, and history are durable|
|Validation|Lab Reset / End-to-End Regression Testing|Real PA-440 workflow can be repeated safely in the lab|
|Lifecycle|RMA / Decommission Planning|Replacement and retirement processes reuse the same architecture|

---
# 2\. Proposed Epic

## New Store PA-440 — Strata Cloud Manager Build Automation

### Goal

Replace Panorama-dependent new-store firewall onboarding/build steps with an SCM-based workflow while preserving existing store assignment, StoreData, deployment, reporting, and operational support capabilities.

### Guiding Principles

* The lifecycle is independent of any single orchestration platform.
* Manual procedures remain documented and supported.
* Dashboard one-off actions and automation should use the same reusable operations.
* State transitions must be verified before the workflow advances.
* New Store, RMA, and Decommission are separate workflows that reuse common building blocks.
* PSU is the current orchestration platform, not the definition of the process.

---
# 3\. Proposed Jira Workstreams

## Workstream 1 — Document SCM New-Store Architecture

### Outcome

Create and maintain the architecture reference for the SCM new-store firewall lifecycle.

### Includes

* High-level lifecycle
* Local staging vs. SCM tenant boundary
* Manual vs. dashboard vs. automated execution model
* Lifecycle principles
* Integration points
* Open decisions
* Links to supporting engineering references

### Current State

Substantially complete / ready for stakeholder review.

---
## Workstream 2 — Validate SCM Store Configuration Model

### Outcome

Confirm how common and store-specific firewall configuration is represented in SCM.

### Includes

* Store folder inheritance
* Serial-specific `snp-{serial}` model
* Store-specific variables
* Variable types
* Device-scoped effective values
* Folder / snippet relationships

### Current State

Substantially complete.

---
## Workstream 3 — Firewall Intake \& Read-Only Discovery

### Outcome

Reliably discover a staged PA-440 and determine its current state without mutating it.

### Includes

* Serial
* Hostname
* Model
* PAN-OS version
* Content version
* Panorama state
* Advanced Routing configured state
* Advanced Routing running state
* Cloud-management enabled state
* Cloud connection state
* Safe handling of unknown / failed reads

### Acceptance

A firewall can be classified into the next required lifecycle action based on observed state.

---
## Workstream 4 — Software \& Content Staging

### Outcome

Bring a staging firewall to the approved software and content baseline.

### Includes

* PAN-OS target comparison
* Upgrade sequencing
* Content validation
* Reboot handling where required
* Post-change rediscovery

### Acceptance

The workflow does not advance until the firewall reports the approved baseline.

---
## Workstream 5 — Advanced Routing Preparation

### Outcome

Enable and verify Advanced Routing using the supported firewall lifecycle.

### Includes

* Configure `advance-routing`
* Commit
* Reboot
* Wait for management availability
* Verify operational routing state
* Distinguish configured vs. running state

### Acceptance

Advanced Routing is both configured and operational before the workflow advances.

---
## Workstream 6 — Cloud Management Enablement

### Outcome

Place the firewall into cloud-management mode and verify the local state.

### Includes

* Enable cloud service
* Commit
* Rediscover
* Verify local cloud-management state
* Handle conflicting / unknown states

### Acceptance

Cloud management is verified locally before SCM onboarding continues.

---
## Workstream 7 — SCM API Foundation

### Outcome

Create reusable SCM API functions independent of dashboard or orchestrator.

### Initial Capabilities

* Authenticate to SCM
* Read devices
* Read folders
* Read snippets
* Read variables
* Read connection state
* Read push/job state

### Acceptance

SCM tenant state can be queried from automation without relying on GUI inspection.

---
## Workstream 8 — SCM Device Onboarding

### Outcome

Claim and connect a staged firewall to SCM.

### Includes

* Device claim / registration
* SCM device lookup
* Connection verification
* Configuration scope if required
* Target folder placement
* Display name
* Bounded retries / timeouts

### Acceptance

The firewall is visible and verified connected in SCM before store configuration is applied.

---
## Workstream 9 — Platform-Neutral Store Desired State

### Outcome

Represent the desired store firewall configuration independently of Panorama or SCM.

### Proposed Function

`Get-DSGFirewallStoreConfiguration`

### Inputs

* Store number
* Canonical StoreData

### Outputs

Store-specific values such as:

* `$loopback1`
* `$store-net`
* `$store-pos`
* `$ae1-222`
* `$ae1-555`
* `$netflowIP`

### Acceptance

The same desired-state output can be used by reporting, reconciliation, manual operations, and automation.

---
## Workstream 10 — SCM Snippet / Variable Reconciliation

### Outcome

Create or reconcile the serial-specific SCM configuration for a store firewall.

### Includes

* Find or create `snp-{serial}`
* Read current variables
* Compare desired vs. effective values
* Update only on drift
* Associate snippet to the device

### Acceptance

Repeated execution is idempotent and produces no unnecessary changes.

---
## Workstream 11 — Preserve Store ↔ Serial Assignment Integration

### Outcome

Ensure existing store-build systems can continue assigning a firewall serial without depending on Panorama.

### Includes

* Existing `/palo/store_assignments` consumers
* NetBox store-build integration
* Dashboard assignment path
* Duplicate/conflict detection
* Future RMA replacement behavior

### Acceptance

Existing upstream store-build workflows continue to produce the canonical Store ↔ Serial assignment consumed by the SCM workflow.

---
## Workstream 12 — SCM Push \& Effective-State Verification

### Outcome

Push desired configuration and prove that SCM/device state matches the intended result.

### Includes

* Conflict checks
* Push initiation
* Parent job polling
* Sub-job polling
* Failure details
* Config Sync / effective-state verification
* Retry / timeout handling

### Acceptance

A successful API call or completed job alone does not mark the firewall complete.

---
## Workstream 13 — Dashboard 2.0 / Operator Experience

### Outcome

Provide a lifecycle-oriented operational interface without making the dashboard itself the definition of the process.

### Capabilities

* Current lifecycle stage
* Observed state
* Desired state
* Next action
* One-off approved actions
* Active job
* Retry state
* History
* Error / hold reason
* Final readiness state

### Design Requirement

The dashboard should consume stable APIs/data contracts so it can move from PSU v3 to PSU v5 or another orchestrator with minimal workflow redesign.

---
## Workstream 14 — Manual New-Store Runbook

### Outcome

Network Engineering and Store Projects have a supported reference process even when automation is unavailable.

### Includes

* Prerequisites
* Required inputs
* Manual staging sequence
* SCM onboarding sequence
* Store configuration
* Verification steps
* Recovery / escalation notes
* Dashboard one-off usage where available

### Acceptance

An engineer can understand and perform the supported process without requiring the automated orchestrator.

---
## Workstream 15 — Durable Workflow State / Audit History

### Outcome

Track lifecycle progress independently of transient orchestration jobs.

### Includes

* Device workflow state
* Current stage
* Next action
* Active job ID
* Retry count
* Lock / lease information
* Last observed state
* Action history
* Failure details

### Acceptance

A restarted or failed orchestrator does not lose the authoritative workflow state.

---
## Workstream 16 — Lab Reset \& End-to-End Regression Testing

### Outcome

Provide a repeatable real-hardware validation loop using approved lab PA-440 devices.

### Proposed Test Cycle

```text
Factory Reset
→ USB Bootstrap
→ DHCP / Base Config
→ Discovery
→ PAN-OS / Content
→ Advanced Routing
→ Cloud Management
→ SCM Onboarding
→ Store Configuration
→ Push / Verification
→ Reset and repeat
```

### Acceptance

The lifecycle can be executed repeatedly against real hardware with consistent results.

---
## Workstream 17 — Pilot \& Production Cutover

### Outcome

Move from engineering validation to supported new-store production use.

### Includes

* Pilot device/store selection
* Manual fallback procedure
* Success criteria
* Failure handling
* Stakeholder signoff
* Production enablement
* Panorama dependency removal from the new-store path

---
# 4\. Lifecycle Extensions

## RMA / Replacement

RMA is expected to be a separate workflow because the store SCM configuration already exists.

Current working model:

```text
Replacement PA-440
→ Standard Staging
→ Cloud / SCM Connection
→ Locate Existing Store Configuration
→ Attach Replacement Serial
→ Recreate / Reassociate Serial-Specific Snippet
→ Push / Verify
→ Retire Old Serial
```

Detailed behavior remains subject to stakeholder validation and the supported RMA process.

---
## Decommission / Retirement

Decommission is the reverse lifecycle problem and should address:

* SCM device association cleanup
* Snippet / variable retention or deletion
* Device unclaim behavior
* Inventory / NetBox updates
* Audit history
* Reporting state
* Retention requirements

This should be planned separately from new-store implementation.

---
# 5\. Stakeholder Decisions Needed

The following decisions should be resolved or assigned during stakeholder review:

1. Confirm the supported new-store lifecycle.
2. Confirm the greenfield SCM onboarding order.
3. Define the exact meaning of **Build Complete**.
4. Confirm the canonical Store ↔ Serial assignment source.
5. Confirm ownership of StoreData changes.
6. Confirm ownership of SCM folder/snippet standards.
7. Confirm who owns the supported manual new-store procedure.
8. Confirm who owns the supported RMA procedure.
9. Confirm which dashboard one-off actions should be available.
10. Confirm pilot criteria and production cutover expectations.
11. Confirm whether lifecycle state/history should remain durable outside the orchestrator.
12. Confirm expectations for RMA and decommission documentation before automation work begins.

---
# 6\. Relationship to Detailed Engineering Jira

This document is the stakeholder-facing work breakdown.

Detailed engineering Jira items may be created beneath these workstreams for:

* API functions
* PowerShell modules
* PSU jobs
* SQL schema
* unit/offline tests
* lab validation
* documentation
* dashboard pages
* error handling
* migration compatibility
* production rollout

The detailed Jira hierarchy should preserve the lifecycle phase names above so implementation work remains traceable to the supported process.

---
# 7\. Related Documents

* [SCM New Store Firewall Lifecycle](SCM-New-Store-Firewall-Lifecycle.md)
* [SCM New Store Manual Process](SCM-New-Store-Manual-Process.md)
* [SCM RMA Process](SCM-RMA-Process.md)
* [SCM Decommission Process](SCM-Decommission-Process.md)
* [SCM Migration Ansible Reference Analysis](SCM-Migration-Ansible-Reference-Analysis.md)
* [SCM Open Questions](SCM-Open-Questions.md)

