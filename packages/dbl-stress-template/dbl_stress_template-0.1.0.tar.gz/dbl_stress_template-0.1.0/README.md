# dbl-stress-template

[![CI](https://github.com/lukaspfisterch/dbl-stress-template/actions/workflows/tests.yml/badge.svg)](https://github.com/lukaspfisterch/dbl-stress-template/actions/workflows/tests.yml)
![PyPI](https://img.shields.io/pypi/v/dbl-stress-template.svg)
![Python](https://img.shields.io/pypi/pyversions/dbl-stress-template.svg)

dbl-stress-template is a small diagnostic template for stress-testing real systems against DBL invariants.
It helps you locate where normativity enters, what is treated as authority, and whether replay is possible.
It is not a framework and not a product. It is a repeatable analysis scaffold.
Use it to surface implicit decisions, observation leaks, and non-replayable state.
The template is designed to map directly onto DBL artifacts: L, G, V, DECISION, PROOF, EXECUTION.

## The 5-field stress frame
1) Trigger
2) Normative Question
3) Authority
4) Irreversibility
5) Replay Requirement

## Compact examples

Access decision (ALLOW or DENY)
- Trigger: request to access a protected resource
- Normative Question: is access permitted
- Authority: policy version and admitted inputs (L)
- Irreversibility: access once granted can leak data
- Replay Requirement: decision must be reproducible from V

Irreversible deletion
- Trigger: delete request
- Normative Question: is deletion permitted
- Authority: policy version and admitted inputs (L)
- Irreversibility: deletion cannot be undone
- Replay Requirement: decision and justification must be reconstructible

## What this is not
- Not a policy engine
- Not a governance framework
- Not a runtime or integration layer
- Not a compliance product

## How to use this with DBL
- Trigger maps to INTENT creation and L admission.
- Normative Question must be resolved only via DECISION events.
- Authority must be admitted by L and consumed by G, never from observations.
- Irreversibility increases the need for explicit DECISION and stable policy versions.
- Replay Requirement must be satisfied by V alone, using DECISION and PROOF separation.
