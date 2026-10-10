# Implementation Plan: RFQ Combo Price Waterfall

**Branch**: `spec/001-price-waterfall` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-price-waterfall/spec.md`

## Summary

Build a stateless analytics web application that values a two-to-four-leg RFQ combo and returns one
explainable price-waterfall response. A Python 3.12/FastAPI backend owns validation, settlement-state
enumeration, the independence baseline, a settlement-aware Gaussian-copula adjustment, effective-dated
fee assessment, historical validation, and deterministic fixtures. A strict TypeScript/Next.js frontend
renders the returned stages and provenance without reproducing calculations or persisting analysis data.

For at most four legs, both independent and correlated expected payoff are computed over the complete
set of at most 16 joint settlement states. Historical observations are first mapped through each leg's
threshold, direction, and settlement rule; the resulting binary outcomes drive latent correlation
estimation. Fee calculations use verified, effective-dated policy evidence and become unavailable when
scope or RFQ-role applicability cannot be established.

## Technical Context

**Language/Version**: Python 3.12+; TypeScript in strict mode on a supported Next.js/Node.js release

**Primary Dependencies**: FastAPI, Pydantic, Pandas, NumPy, SciPy, Uvicorn; Next.js, React,
`openapi-typescript`, and `openapi-fetch`

**Storage**: No database, user session store, analysis history, or browser persistence. Versioned public
demo fixtures and verified fee-policy snapshots are repository files; any live public-data cache is
identity-independent and excludes request and result data.

**Testing**: pytest, HTTPX/TestClient, Ruff, mypy; Vitest, React Testing Library, Playwright, ESLint,
Prettier, TypeScript compiler, OpenAPI drift checks

**Target Platform**: Linux-hosted stateless HTTP service and modern evergreen browsers; local demo must
remain fully operable without network access by selecting the deterministic fixture

**Project Type**: Web application with separate backend and frontend applications in one repository

**Performance Goals**: At least 95% of valid demo analyses complete and render within 3 seconds under
single-presenter conditions; canonical deterministic analysis is byte-for-byte stable across 10 runs
under the pinned model/runtime version

**Constraints**: Two to four legs; no trade execution; one coherent API response; no analysis payloads
in URLs, logs, external services, caches, or persistent storage; decimal-safe monetary boundaries;
explicit units, provenance, classifications, fee verification, numerical tolerances, and fallback state;
unsupported structures and materially incoherent dependence inputs fail without a fabricated value

**Scale/Scope**: One anonymous user at a time, one primary analysis screen, one canonical deterministic
scenario, best-effort live public data, a documented supported payoff subset, and concise walk-forward
historical-validation summaries for a 36-hour hackathon release

**Reference Reuse Policy**: SnapCast is a read-only design reference. Because its repository is
proprietary, Parity will not copy its code or depend on its package. Generic patterns selected in
`research.md` will be independently implemented and tested for financial contracts; sports rules,
cross-game independence, stored analysis history, and PrizePicks payout logic are explicitly excluded.

## Constitution Check

*GATE: Passed before Phase 0 research; passed again after Phase 1 design.*

| Gate | Design response | Status |
|------|-----------------|--------|
| Decision support, not truth | Contract classifies every value and requires estimate/no-guarantee disclosures; quote difference is side-relative, never guaranteed profit. | PASS |
| API-first architecture | FastAPI owns all calculations; `contracts/openapi.yaml` is defined before frontend work and generates strict frontend types. | PASS |
| Statistical integrity and reproducibility | Settlement-aware outcomes, distinct waterfall stages, disclosed Gaussian-copula assumptions, bounded matrix repair, pinned integration settings, and walk-forward validation are explicit. | PASS |
| Type-safe, explicit data | Pydantic boundaries, strict TypeScript, UTC timestamps, bounded probabilities, decimal-string currency, and named units are specified. | PASS |
| Testing is delivery | Contract, quantitative, edge, deterministic, privacy, fallback, rendering, and time-order tests are required by the quickstart. | PASS |
| Simple domain-oriented code | Pure domain modules separate settlement, pricing, correlation, fees, validation, transport, and presentation; no database or generalized infrastructure. | PASS |
| One contract | A complete response and sanitized error union are defined in OpenAPI; committed deterministic and live-shaped fixtures will enforce compatibility. | PASS |
| Demo-first scope | Only the core waterfall, its provenance, deterministic fallback, and concise validation evidence are planned; execution/auth/portfolio scope is excluded. | PASS |
| Zero-data privacy | Request-local computation, allowlisted metadata logs, no persistent identifiers or client storage, no-store headers, and sentinel privacy tests are designed. | PASS |

No constitution exceptions or complexity waivers are required. The Phase 1 artifacts preserve every
gate: the data model has no persistent user entity, the API is stateless and complete, fee uncertainty
is a first-class union, and the quickstart includes quantitative, privacy, contract, and fallback checks.

## Project Structure

### Documentation (this feature)

```text
specs/001-price-waterfall/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md                 # created later by $speckit-tasks; not created by this plan
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── src/parity/
│   ├── api/                 # FastAPI routes, sanitized errors, cache/privacy headers
│   ├── schemas/             # Pydantic API and external-data boundary models
│   ├── domain/
│   │   ├── settlement.py    # contract transformations and complete state/payoff enumeration
│   │   ├── pricing.py       # independence, adjusted value, quote comparison, waterfall
│   │   ├── correlation.py   # tetrachoric fitting, bounded matrix repair, rectangle probabilities
│   │   ├── fees.py          # effective-dated verified fee resolution
│   │   └── validation.py    # walk-forward splits, embargoes, metrics, optional diagnostics
│   ├── data/
│   │   └── provenance.py    # hashes and manifests for public inputs only
│   ├── services/            # analysis orchestration, allowlisted live data, explicit demo fallback
│   ├── fixtures/            # versioned deterministic inputs and policy evidence
│   └── tools/               # OpenAPI export and fixture verification
└── tests/
    ├── unit/                # hand-worked math, invariants, leakage mutation, provenance
    ├── contract/
    └── integration/         # offline/no-write privacy gates and end-to-end API behavior

frontend/
├── package.json
├── src/
│   ├── app/                 # analysis and validation-summary routes
│   ├── components/          # input, waterfall, provenance, disclosure views
│   └── lib/api/             # generated types and typed client
└── tests/                   # component, contract-fixture, and browser privacy tests

contracts/
├── openapi.json             # generated from FastAPI and checked against design contract
└── fixtures/
    ├── canonical-v1.request.json
    ├── canonical-v1.response.json
    └── live-shaped-v1.response.json
```

**Structure Decision**: Use two independently runnable applications in one repository. The backend is
the sole quantitative authority and exports OpenAPI; the frontend consumes generated types and committed
fixtures. This gives two developers a stable parallel boundary without introducing a database, shared
runtime package, or deployment framework that does not improve the demo. SnapCast contributes design and
test patterns only; no source subtree, storage layer, or runtime dependency is imported from it.

## Complexity Tracking

No constitution violations require justification.
