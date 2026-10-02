# Getting Started with Cortex XSOAR

**Date:** July 9, 2026

## Purpose

This document captures my initial discovery discussion with ChatGPT
about Cortex XSOAR and how it may fit into DSG's migration from Panorama
to Strata Cloud Manager (SCM).

------------------------------------------------------------------------

## What is XSOAR?

The biggest takeaway is that XSOAR should be viewed primarily as an
**orchestration platform**, not a firewall configuration platform.

It coordinates work between multiple systems by:

-   Executing Python scripts
-   Running Ansible playbooks
-   Calling REST APIs
-   Integrating with Terraform where appropriate
-   Maintaining workflow state
-   Coordinating multi-step automation
-   Handling approvals, notifications, and rollback

Think of XSOAR as the conductor of an orchestra while SCM, PSU, Meraki,
NetBox, SolarWinds, and other platforms perform the work.

------------------------------------------------------------------------

## Relationship to PowerShell Universal

One possible architecture is:

``` text
SolarWinds
      │
      ▼
   Webhook
      │
      ▼
XSOAR Playbook
      │
      ├── PSU REST API
      ├── SCM API
      ├── Meraki API
      ├── NetBox
      └── Python / Ansible
```

Rather than replacing mature PSU automation, XSOAR can orchestrate it.

------------------------------------------------------------------------

## Event Driven Automation

SolarWinds or another monitoring platform can generate a webhook when an
event occurs.

Example flow:

1.  SolarWinds detects an issue.
2.  Sends a webhook.
3.  XSOAR starts a playbook.
4.  Runs diagnostics.
5.  Determines remediation.
6.  Executes automation.
7.  Documents the results.

------------------------------------------------------------------------

## Future Agentic AI

Upcoming versions are expected to introduce agentic capabilities that
may:

-   Evaluate context before acting.
-   Select among multiple remediation paths.
-   Reduce rigid workflow logic.
-   Make recommendations based on system state.

------------------------------------------------------------------------

## Example Use Case

SolarWinds identifies a MAC address belonging to a specific device
class.

Desired workflow:

-   Detect device
-   Locate switch and interface
-   Move interface into VLAN 1012
-   Verify success
-   Record completion

------------------------------------------------------------------------

## Zero Touch Deployment

Current understanding:

XSOAR orchestrates provisioning rather than performing it.

Example:

-   Device boots.
-   Temporary Internet access established.
-   XSOAR launches onboarding playbook.
-   Python or Ansible provisions the device.
-   SCM becomes the ongoing management platform.

------------------------------------------------------------------------

## SCM Migration Questions

Questions identified:

-   How do SCM Snippets replace Panorama variables?
-   How are variables passed into Snippets?
-   Which tasks belong in SCM versus XSOAR?

------------------------------------------------------------------------

## Meraki Integration

Current build process requires DHCP reservations from Meraki.

Outstanding questions:

-   Should XSOAR retrieve reservations?
-   Should PSU continue to own this logic?
-   How should the data flow into SCM?

------------------------------------------------------------------------

## Bootstrap Networking Challenge

Store replacements require temporary Internet connectivity for firewall
onboarding.

Possible workflow:

-   Enable temporary Meraki configuration.
-   Allow firewall provisioning.
-   Remove temporary configuration.
-   Continue production deployment.

------------------------------------------------------------------------

## Rollback and State Tracking

An important capability to validate is whether XSOAR can:

-   Track temporary changes.
-   Resume interrupted workflows.
-   Automatically rollback configuration.
-   Ensure cleanup occurs before marking a workflow complete.

------------------------------------------------------------------------

## Follow-up with Foot Locker

Action item:

Meet with Matt (Foot Locker Architect) to learn:

-   Their deployment workflow.
-   Bootstrap networking strategy.
-   XSOAR implementation.
-   Lessons learned.

------------------------------------------------------------------------

## Current Working Assumptions

-   XSOAR = orchestration
-   SCM = firewall management
-   PSU = existing business logic and APIs
-   SolarWinds = monitoring and event generation
-   Meraki = WAN edge and bootstrap networking
-   Python/Ansible = execution layer

These assumptions will evolve as additional research is completed.
