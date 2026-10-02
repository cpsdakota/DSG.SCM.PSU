# SCM Firewall RMA Process



## Status



**Working Draft — Requires validation with Bryan / Firewall Engineering**



This document describes the current proposed RMA workflow based on the known SCM architecture and existing migration/new-store work.



It is not yet the approved operational procedure.



---
## Current Working Assumption



An RMA is expected to differ from a new-store build because the store's SCM configuration already exists.



The replacement firewall should therefore reuse the existing store configuration rather than recreate the store from scratch.



---
## Proposed High-Level Flow



```mermaid

flowchart TD

   A[Replacement PA-440 Received]

   B[USB Bootstrap / Base Configuration]

   C[Stage Firewall]

   D[Upgrade PAN-OS / Content]

   E[Enable Advanced Routing]

   F[Enable Cloud Management]

   G[Claim / Connect Replacement to SCM]

   H[Identify Existing Store SCM Configuration]

   I[Associate Replacement Device]

   J[Recreate or Reassign Serial-Specific Snippet]

   K[Apply Existing Store Variables]

   L[Push Configuration]

   M[Verify Replacement Firewall]

   N[Remove / Retire Old Serial]

   O[RMA Complete]



   A --> B --> C --> D --> E --> F --> G

   G --> H --> I --> J --> K --> L --> M --> N --> O

