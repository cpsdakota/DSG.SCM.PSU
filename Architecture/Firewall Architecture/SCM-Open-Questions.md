## Status Legend



- **OPEN** — unanswered

- **PROPOSED** — working assumption exists

- **VALIDATED** — confirmed with stakeholder / system behavior

- **CLOSED** — documented elsewhere and no longer unresolved



# SCM Firewall Architecture — Open Questions



## Purpose



Track unresolved architecture, operational, ownership, and lifecycle questions for the SCM firewall program.



Questions should remain here until:

- answered,

- documented in the appropriate architecture/process page,

- and reflected in Jira when implementation work is required.



---



## New Store Build



- What is the final approved greenfield SCM onboarding order?

- What exactly constitutes "build complete"?

- At what point is a firewall considered ready for Store Projects?

- What is the supported manual build path if automation is unavailable?

- Which steps require human approval vs. can be fully automated?

- What is the production pilot process before Panorama is removed from the new-store workflow?



---



## SCM Device Onboarding



- What is the supported claim/onboarding method for greenfield PA-440s?

- When should configuration scope be created?

- When should the device be moved to the target folder?

- When should `snp-{serial}` be associated?

- What SCM state definitively proves the firewall is connected?

- Should `is_connected` be required before continuing?

- What retry / timeout behavior is appropriate?



---



## Store Configuration / Desired State



- Is `snp-{serial}` the permanent model for new stores?

- Who owns the snippet naming convention?

- Are all store-specific values expected to live in the serial snippet?

- Should `$netflowIP` become part of the standard StoreData contract?

- Are there any other store-specific values not yet represented?

- What is the authoritative source for Store ↔ Serial assignment?



---



## Manual Process / Operational Ownership



- Who owns the documented manual new-store procedure?

- Who owns the documented RMA procedure?

- What actions must remain possible without PSU?

- Should dashboard actions map one-for-one with the documented manual process?

- What information must Network Engineering and Store Projects be able to see?

- Who approves changes to the documented lifecycle?



---



## RMA



- Does the replacement firewall go through the full staging process?

- Is a new `snp-{newserial}` always created?

- Can the existing snippet be renamed/re-associated?

- When is the old device unclaimed?

- Can old and replacement serials coexist temporarily?

- What store configuration is reused unchanged?

- What is the rollback process if the replacement fails?

- What information is required from Store Projects / vendor / RMA ticket?

- What does "RMA complete" mean operationally?



---



## Decommission / Retirement



- What triggers decommission?

- Should snippets be deleted, archived, or retained?

- Should the firewall be explicitly unclaimed?

- What historical data must be retained?

- What NetBox / inventory updates are required?

- What reporting state represents retired hardware?

- Are there retention or audit requirements?



---



## Dashboard / Operator Experience



- What is the minimum useful Dashboard 2.0?

- Which one-off actions should be exposed?

- Which actions require confirmation or role restrictions?

- Should the dashboard show both observed state and desired state?

- How much history should be retained/displayed?

- How do we keep the UI portable to PSU v5 or another orchestrator?



---



## Workflow State / Automation



- What system owns durable workflow state?

- What states should be lifecycle state vs. workflow execution state?

- What happens when an orchestrator job dies mid-action?

- How are retries bounded?

- What conditions require manual intervention?

- What state must be freshly rediscovered before moving forward?



---



## Testing / Lab



- What is the approved factory-reset / USB-bootstrap test procedure?

- Which lab serials are approved for destructive testing?

- What states should be captured as regression fixtures?

- How many successful end-to-end repetitions are required before pilot?

- What constitutes a failed validation run?



---



## Ownership / Stakeholders



- Who owns SCM tenant standards?

- Who owns new-store firewall workflow approval?

- Who owns RMA workflow approval?

- Who owns Store ↔ Serial assignment data?

- Who owns StoreData changes?

- Who owns lifecycle reporting?

- Who signs off on pilot and production cutover?

