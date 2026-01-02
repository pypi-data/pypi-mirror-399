# DBL Core

[![CI / Tests](https://github.com/lukaspfisterch/dbl-core/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lukaspfisterch/dbl-core/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/dbl-core.svg?label=PyPI)](https://pypi.org/project/dbl-core/)
[![Python >=3.11](https://img.shields.io/pypi/pyversions/dbl-core.svg?label=Python)](https://pypi.org/project/dbl-core/)
[![Typing: Typed](https://img.shields.io/pypi/typing/dbl-core.svg?label=Typing)](https://pypi.org/project/dbl-core/)

DBL Core is a deterministic event substrate for the Deterministic Boundary Layer (DBL). It records intent, decisions, and executions as a single ordered stream.

## Why DBL Core exists

DBL Core exists to provide a deterministic, audit-stable event substrate for systems that need to separate:

- intent from decision
- decision from execution
- normative history from observational artifacts

It is designed for systems where replayability, auditability, and governance correctness matter more than convenience or performance.

## Mental Model

DBL Core maintains a single append-only event stream V:

INTENT → DECISION → (optional) EXECUTION → (optional) PROOF

Only DECISION events are normative.
All other data is treated as observational and excluded from digests.

## Scope
- Single-stream event model with deterministic t_index.
- Canonical serialization and digest for events and behavior logs.
- Gate decision events (ALLOW or DENY) as explicit Deltas.
- Embeds kernel traces as observational artifacts with canonical integrity digests.

## Non-Goals
- No policy engine or templates.
- No execution of user tasks.
- No orchestration, UX flows, or intelligence.
- No time, randomness, or I/O side effects.

## What DBL Core is not

DBL Core is intentionally minimal.
It is not:

- a workflow engine
- a policy engine
- a domain framework
- an execution orchestrator
- an LLM wrapper

If you need domain semantics, validation, or verdict logic,
implement a domainrunner on top of DBL Core.

## Contract-first design

DBL Core behavior is defined by a stable, normative contract.

- Code must conform to the contract.
- Tests enforce contract invariants.
- Domain-specific semantics are explicitly out of scope.

See:
- [DBL Core Contract](docs/dbl_contract.md)
- [Domainrunner Contract](docs/dbl_contract_domainrunner.md)

## Contract
- [DBL Core Contract](docs/dbl_contract.md)

## Install

```bash
pip install dbl-core
```
Requires kl-kernel-logic>=0.5.0 and Python 3.11+.

## Public API
- DblEvent, DblEventKind
- BehaviorV
- GateDecision
- normalize_trace

## Ordering
Ordering is derived from t_index (position in V). Timestamps and runtime fields are observational only.

