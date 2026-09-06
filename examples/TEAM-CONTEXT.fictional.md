# Team context — FICTIONAL EXAMPLE

This is invented starter content for a fictional product, Parcel Desk. It does
not describe the repository author's team. Replace every detail before using it.

- Maintainer: Fulfillment team lead
- Last reviewed: 2026-09-06 (example date)
- Review again: 2026-10-06, or when the export migration completes
- Team: four engineers; one rotating support engineer each week

## Critical paths and language

- `checkout.py → limits.py`: a cart must never exceed its configured capacity.
  “Capacity” means the maximum number of items accepted for fulfillment.
- `billing/`: retries must not charge a customer twice. A payment attempt is not
  a completed payment; preserve those distinct terms.

## Ownership

- Checkout: Fulfillment team; backup: the weekly support engineer.
- Billing: Payments team; escalate contract changes to its on-call role.
- Legacy export: one primary maintainer with a trained backup. Single-author
  changes here are intentional; verify backup readiness before inferring a silo.

## Accepted tradeoffs

- `legacy/exporter.py` may query the reporting table directly until migration.
  Read-only SELECTs only; no writes and no customer credential access.
- Revisit at migration completion or before adding a second consumer. In a real
  repository, link the architectural decision here rather than copying its history.

## Constraints

- Existing CSV column order is a public integration contract; append new columns.
- Checkout and billing changes need a human review before merge. Generated
  documentation updates may self-merge after checks pass.
- Support interruptions reduce available reviewers; investigate waiting time
  alongside the support rotation before treating it as disengagement.
