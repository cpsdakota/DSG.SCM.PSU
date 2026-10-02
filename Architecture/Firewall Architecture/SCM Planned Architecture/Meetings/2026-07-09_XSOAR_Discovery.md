# XSOAR Discovery

**Date:** 2026-07-09

------------------------------------------------------------------------

# Purpose

This document captures information gathered during discussions with Palo
Alto Networks regarding Cortex XSOAR and its potential role in the
DICK'S Sporting Goods / Foot Locker firewall migration initiative. The
intent is to document discoveries, assumptions, open questions, and
architectural decisions as they evolve.

------------------------------------------------------------------------

# Background

As part of the DICK'S Sporting Goods acquisition of Foot Locker,
engineering teams are evaluating opportunities to consolidate vendors,
licensing, and operational tooling.

One area under evaluation is Palo Alto Networks lifecycle management and
automation.

Foot Locker currently utilizes **Cortex XSOAR** for portions of their
operational workflow. Initial discussions indicate that XSOAR may become
a significant component of the future automation strategy rather than
building all automation directly against Palo Alto SCM APIs.

------------------------------------------------------------------------

# Meeting Summary

## Licensing

Current understanding:

-   Approximately **five XSOAR licenses** may become available for
    engineering use.
-   One of my immediate objectives is determining whether I will receive
    access to one of these licenses.
-   Licensing availability will influence which automation platform
    becomes the primary development target.

**Status:** Pending confirmation.

------------------------------------------------------------------------

## Foot Locker Environment

Current state:

-   Foot Locker currently operates **XSOAR on-premises**.
-   Their engineering team is planning a migration to a cloud-hosted
    deployment.

Unknowns:

-   Cloud migration timeline
-   Whether DSG engineering can leverage the existing on-prem
    environment
-   When cloud access will become available
-   Whether automation development should wait for the cloud migration

**Action Item**

Determine:

-   Planned migration date
-   Expected cloud availability
-   Whether development can begin prior to migration

------------------------------------------------------------------------

# Automation Discussion

Potential automation areas discussed include:

-   Palo Alto firewall lifecycle management
-   Meraki integration
-   License management
-   Device provisioning
-   Store deployment workflows
-   Future end-to-end orchestration

One of the more interesting observations from the discussion was that
XSOAR may already contain mature playbooks that perform many of the
operations I had been planning to build directly inside SCM.

If those workflows already exist, the project should prioritize reusing
vendor-supported automation instead of recreating similar functionality.

------------------------------------------------------------------------

# Requested Information

The following information has been requested from Palo Alto:

-   XSOAR case studies
-   Lifecycle management documentation
-   Existing playbooks
-   API documentation
-   Customer implementation examples
-   Automation best practices

Brenton also plans to schedule a technical discussion with a XSOAR
specialist to review:

-   Platform capabilities
-   Typical deployment models
-   API integration
-   Playbook architecture
-   Recommended implementation patterns

------------------------------------------------------------------------

# Manual vs API Operations

One concern raised during the discussion involved licensing workflows.

Current understanding:

Some licensing activities appear to require manual interaction through
the Palo Alto portal.

However, it was suggested that APIs may support automating these
operations.

This remains unverified.

## Action Item

Determine:

-   Which licensing operations require manual interaction.
-   Which operations are API accessible.
-   Whether a completely automated provisioning workflow is possible.

------------------------------------------------------------------------

# Architectural Observation

Brenton's recommendation was essentially:

> Leave SCM focused on device management and leverage XSOAR for
> orchestration whenever possible.

The reasoning is that XSOAR may already provide:

-   Proven playbooks
-   Vendor-supported workflows
-   Lifecycle automation
-   Error handling
-   Operational best practices

This could significantly reduce custom development effort.

------------------------------------------------------------------------

# Strategic Direction

This conversation introduced a possible shift in architecture.

Instead of viewing SCM as the primary automation engine, a layered
architecture may provide a better long-term solution.

Possible model:

``` text
Business Workflow
        │
        ▼
    Cortex XSOAR
        │
        ▼
 Palo Alto SCM APIs
        │
        ▼
Firewall Configuration
```

This architecture would allow automation to focus on business intent
rather than individual firewall operations.

Examples:

Instead of:

> Create temporary firewall rule

The workflow becomes:

> Enable temporary store connectivity for deployment.

Instead of:

> Create security policy

The workflow becomes:

> Prepare store for installation.

The orchestration layer determines the technical implementation.

------------------------------------------------------------------------

# Benefits Being Evaluated

Potential advantages include:

-   Less custom code
-   Vendor-supported workflows
-   Faster implementation
-   Easier maintenance
-   Better lifecycle management
-   Consistent operational processes
-   Improved abstraction from low-level Palo Alto APIs

------------------------------------------------------------------------

# Open Questions

## Licensing

-   Will I receive an XSOAR license?
-   How many licenses will be available?
-   What permissions will those licenses include?

## Environment

-   When will Foot Locker migrate XSOAR to the cloud?
-   Can DSG leverage the current environment?
-   Will development wait for cloud migration?

## Automation

-   Which playbooks already exist?
-   Which workflows should remain inside SCM?
-   Which workflows belong in XSOAR?
-   How extensible are existing playbooks?

## APIs

-   Can licensing be automated?
-   Which portal functions expose APIs?
-   Are there API limitations that require manual intervention?

------------------------------------------------------------------------

# Initial Assessment

Current opinion after today's discussion:

Rather than building every workflow directly against SCM APIs, it may be
more valuable to leverage XSOAR as the orchestration platform whenever
it already provides mature, supported functionality.

Doing so would:

-   Reduce engineering effort
-   Improve maintainability
-   Leverage Palo Alto best practices
-   Keep custom automation focused on business processes instead of
    firewall implementation details

This aligns well with the long-term architectural goal of building
automation around **desired business outcomes**, while allowing vendor
platforms to handle the low-level implementation whenever practical.

------------------------------------------------------------------------

# Next Steps

-   [ ] Confirm XSOAR licensing availability.
-   [ ] Meet with the Palo Alto XSOAR specialist.
-   [ ] Review provided case studies and documentation.
-   [ ] Evaluate existing playbooks.
-   [ ] Verify API support for licensing operations.
-   [ ] Determine Foot Locker cloud migration timeline.
-   [ ] Compare XSOAR, SCM, and hybrid architectural approaches.
-   [ ] Update the overall SCM Planned Architecture documentation with
    findings.
