# Parity Constitution

## Core Principles

### I. Decision Support, Not Objective Truth
Parity MUST present every calculated value as a model estimate, not an objectively correct
probability, guaranteed return, or trading recommendation. User-facing language MUST distinguish
observed market data, model-derived values, simulated inputs, and unavailable data. An RFQ quote
premium MUST describe the difference between a quote and Parity's estimate; it MUST NOT be labeled
as guaranteed market-maker profit. Rationale: honest framing is a product requirement for a
financial analytics tool, not optional copy polish.

### II. API-First Architecture
The backend MUST own pricing, statistical, fee, and validation logic behind a documented HTTP API.
An API contract MUST be defined before dependent frontend work begins and MUST specify request and
response schemas, units, nullability, error shapes, and data provenance. The Next.js frontend MUST
consume this contract and MUST NOT reimplement quantitative calculations. Breaking contract changes
require explicit coordination between both developers. Rationale: a stable contract lets frontend
and backend development proceed in parallel during the hackathon.

### III. Statistical Integrity and Reproducibility
The four-part price waterfall MUST keep the independence baseline, correlation adjustment, RFQ
quote premium, and fees visible as distinct steps. Correlation modeling MUST reflect the underlying
outcomes, contract thresholds, and settlement rules; raw market-price correlation alone is not a
sufficient substitute. Gaussian-copula assumptions, sample windows, missing-data handling, and
estimation limitations MUST be disclosed. Historical validation MUST use only information available
at the evaluated time and MUST prevent look-ahead bias. Identical inputs and configuration MUST
produce identical outputs. Rationale: statistical sophistication is valuable only when assumptions
and limitations remain inspectable.

### IV. Type-Safe, Explicit Data
Python code MUST use type annotations and Pydantic models at API and external-data boundaries.
TypeScript MUST run in strict mode; unexplained `any`, unvalidated type assertions, and implicit
nullable states are prohibited. Probability, price, fee, timestamp, settlement, and provenance
fields MUST use unambiguous names and documented units. Monetary values MUST use integer minor units
or decimal-safe representations; floating-point values are acceptable for statistical computation
when conversion and rounding boundaries are explicit. Rationale: type and unit ambiguity can turn a
plausible result into a materially incorrect financial display.

### V. Testing Is a Delivery Requirement
Every pricing rule, statistical transformation, fee calculation, and API schema change MUST include
pytest coverage before it is considered complete. Tests MUST cover normal cases, boundary values,
invalid inputs, missing live data, non-binary or unsupported settlement structures, and deterministic
demo fixtures. Historical-validation tests MUST demonstrate time-ordered fitting and evaluation.
Frontend work MUST test the critical price-waterfall rendering and API error/fallback states at the
lightest level that gives reliable hackathon feedback. A passing focused test suite is required
before merging. Rationale: a polished demo cannot compensate for incorrect quantitative outputs.

### VI. Simple, Readable, Domain-Oriented Code
Code MUST favor small pure functions for quantitative transformations, explicit domain names, and
clear separation among data acquisition, modeling, fee logic, API transport, and presentation.
Python MUST follow standard formatting and import conventions; TypeScript and React MUST follow the
repository's automated formatter and linter once selected. Public functions and non-obvious formulas
MUST document inputs, outputs, units, and assumptions. Premature abstractions, generic frameworks,
and infrastructure without a demonstrated demo need are prohibited. Rationale: two developers must
be able to review and change each other's work safely within 36 hours.

### VII. One Contract Across Frontend and Backend
The backend's OpenAPI schema MUST be the integration source of truth. Shared frontend types SHOULD
be generated from that schema; if generation is impractical during the hackathon, manually defined
types MUST be checked against contract fixtures. The API MUST return the complete waterfall and its
metadata in one coherent response so the frontend can explain each adjustment without reverse
engineering it. Contract fixtures MUST include both live-data-shaped and deterministic-demo-shaped
responses. Rationale: integration failures are most likely at schema, unit, and fallback boundaries.

### VIII. Demo-First Scope Discipline
The team MUST optimize for one credible end-to-end RFQ combo analysis flow. Real-money execution,
portfolio custody, production authentication, generalized trading infrastructure, and speculative
scalability work are out of scope. Live public market data SHOULD be used where practical, but every
external dependency MUST have a clearly labeled deterministic fallback. Any proposed feature MUST
either improve the core waterfall demo, its correctness, or its explainability; otherwise it is
deferred. Rationale: reliable completion is more valuable than breadth in a 36-hour hackathon.

## Product and Technical Constraints

- The supported stack is Python 3.12+, FastAPI, Pydantic, Pandas, NumPy, SciPy, pytest, Next.js,
  React, and TypeScript. Adding a dependency requires a concrete reduction in delivery risk or
  implementation effort.
- Parity provides analytics only. It MUST NOT place, route, or simulate the successful execution of
  real-money trades.
- The model MUST NOT assume every Kalshi combo leg or payoff is simple binary settlement. Inputs MUST
  represent relevant thresholds, directions, settlement rules, and payoff structure; unsupported
  structures MUST return a clear limitation rather than a fabricated value.
- Fees MUST come from a verified, documented rule or source. If an applicable fee cannot be verified,
  the response MUST mark it as unknown or estimated and identify the assumption; unsupported fee
  constants MUST NOT be presented as authoritative.
- Every waterfall result MUST carry enough provenance to identify the input source, observation time,
  model/configuration version, whether values are live or simulated, and any fallback used.
- The demo MUST remain operable without live market data by using versioned deterministic fixtures.
  Simulated or estimated values MUST be visibly labeled in both API responses and the UI.
- Secrets, API credentials, and user-identifying data MUST never be committed. Only the minimum public
  market data needed for the demo may be stored locally.

## Development Workflow and Quality Gates

1. Work MUST follow the Spec Kit sequence: constitution, specification, plan, tasks, implementation.
   A phase begins only after the preceding artifact has been reviewed by the team.
2. Feature behavior and acceptance criteria MUST be settled in the specification before architecture
   is committed in the plan. Implementation MUST NOT begin from an unreviewed task list.
3. Frontend and backend developers MUST agree on the API contract and deterministic fixtures before
   building dependent UI and service paths. Contract changes MUST be reviewed by both developers.
4. Work MUST occur on short-lived branches and enter `main` through a reviewed pull request. Pull
   requests MUST state which specification requirement they satisfy and identify model or data
   assumptions that changed.
5. Before merge, relevant formatting, type checks, and tests MUST pass. A temporary exception requires
   both developers' agreement, a documented reason, and a bounded follow-up; correctness and
   disclosure tests are never waivable.
6. Reviews MUST verify quantitative assumptions, time ordering, units, user-facing claims, contract
   compatibility, and deterministic fallback behavior in addition to ordinary code quality.
7. When time forces a tradeoff, the team MUST preserve correctness, disclosure, and a working
   deterministic demo before visual polish, additional markets, or infrastructure.

## Governance

This constitution is the highest-authority development policy for Parity. Specifications, plans,
tasks, code reviews, and implementation decisions MUST comply with it. If another project document
conflicts with this constitution, the constitution controls until it is formally amended.

Amendments require a written proposal, review by both developers, an explanation of affected
artifacts or code, and a semantic version change. MAJOR versions remove or redefine a governing
principle incompatibly; MINOR versions add a principle or materially expand mandatory guidance;
PATCH versions clarify wording without changing obligations. The ratification date remains fixed;
the last-amended date changes with every approved amendment.

Each Spec Kit phase review and each pull request review MUST include a constitution compliance check.
Deviations MUST be explicit, narrowly bounded, and approved by both developers; no deviation may
misrepresent model certainty, financial outcomes, fee accuracy, data provenance, or demo inputs.

**Version**: 1.0.0 | **Ratified**: 2026-10-10 | **Last Amended**: 2026-10-10
