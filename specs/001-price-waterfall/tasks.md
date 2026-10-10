---

description: "Implementation tasks for the RFQ combo price waterfall"
---

# Tasks: RFQ Combo Price Waterfall

**Input**: Design documents from `/specs/001-price-waterfall/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/openapi.yaml`, and `quickstart.md`

**Tests**: Tests are mandatory under Constitution Principle V. Within each story, create the listed
tests first, confirm that they fail for the intended reason, and then implement the behavior.

**Organization**: Tasks are grouped by user story so the core demo can ship before secondary evidence
features. `[P]` means the task can run in parallel with adjacent `[P]` tasks because it owns different
files and has no incomplete dependency. Every task includes its intended file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the smallest independently runnable backend/frontend workspace and quality-tool baseline.

- [x] T001 Create the planned `backend/src/parity/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`, `contracts/fixtures/`, and `contracts/` directory structure with package marker files only where Python requires them
- [x] T002 [P] Configure Python 3.12, FastAPI, Pydantic, NumPy, Pandas, SciPy, HTTPX, Uvicorn, pytest, Hypothesis, Ruff, and mypy in `backend/pyproject.toml`
- [x] T003 [P] Configure Next.js, strict TypeScript, React, `openapi-typescript`, `openapi-fetch`, ESLint, Prettier, Vitest, Testing Library, and Playwright in `frontend/package.json`, `frontend/tsconfig.json`, and the corresponding tool config files
- [x] T004 [P] Add repository-level developer commands for backend checks, frontend checks, API generation, and the offline demo in `Makefile` without adding deployment or database infrastructure
- [x] T005 Validate `specs/001-price-waterfall/contracts/openapi.yaml` as OpenAPI 3.1, remove any duplicate YAML keys, and preserve the approved request, response, error, and privacy-header semantics

**Checkpoint**: Both applications install independently, their empty quality gates run, and the design
contract passes schema validation.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the type, API, privacy, and contract boundaries required by every user story.

**Critical**: No user-story implementation starts until this phase is complete.

- [x] T006 [P] Define shared enums, decimal-string boundaries, classified-value unions, and provenance schemas with forbidden extra fields in `backend/src/parity/schemas/common.py`
- [x] T007 [P] Define condition, contract-leg, combo, quote, market-input-mode, and analysis request schemas with cross-field invariants in `backend/src/parity/schemas/analysis.py`
- [x] T008 [P] Define correlation, fee, waterfall, validation-summary, analysis-response, and sanitized error schemas in `backend/src/parity/schemas/results.py`
- [x] T009 Add schema-boundary tests for ranges, timezone-aware timestamps, unique legs, complete state tables, decimal money, and forbidden extras in `backend/tests/unit/test_schemas.py`
- [x] T010 [P] Create the FastAPI application and health route in `backend/src/parity/api/app.py` and `backend/src/parity/api/routes/health.py`
- [x] T011 [P] Implement allowlisted metadata-only logging, sanitized exception mapping, and no-store response headers in `backend/src/parity/api/privacy.py` and `backend/src/parity/api/errors.py`
- [ ] T012 Add sentinel tests proving request bodies, quote values, results, and personal identifiers are absent from success and error logs in `backend/tests/integration/test_logging_privacy.py`
- [x] T013 Implement deterministic OpenAPI export and drift checking in `backend/src/parity/tools/export_openapi.py`, generating `contracts/openapi.json` from FastAPI
- [x] T014 Generate strict frontend API types in `frontend/src/lib/api/generated.ts` and add the reproducible generation/drift command to `frontend/package.json`
- [x] T015 Implement the no-credentials typed HTTP client with explicit success/error unions in `frontend/src/lib/api/client.ts`
- [ ] T016 Add backend/frontend contract-shape tests in `backend/tests/contract/test_openapi.py` and `frontend/tests/contract/api-types.test.ts`

**Checkpoint**: The API schema is executable, generated frontend types match it, errors are sanitized,
and neither application has introduced identity, persistence, or payload logging.

---

## Phase 3: User Story 1 — Evaluate a Combo Quote (Priority: P1) MVP

**Goal**: Submit a supported two-to-four-leg combo and receive the complete four-stage waterfall with
correct user-side quote economics and fee treatment.

**Independent Test**: Submit the canonical hand-worked two-leg request and verify the independence
baseline, correlation adjustment, model fair value, quote difference, fee result, and net expected value
with correct signs, units, classifications, and unavailable behavior.

### Tests for User Story 1

- [x] T017 [P] [US1] Add hand-enumerated tests for all-legs-win, OR, XOR, and explicit state-table settlement payoffs in `backend/tests/unit/test_settlement.py`
- [x] T018 [P] [US1] Add correlation tests for identity/independence, positive and negative dependence direction, zero/one marginals, invalid matrices, bounded Higham repair, and state-probability reconciliation in `backend/tests/unit/test_correlation.py`
- [x] T019 [P] [US1] Add hand-worked buy/sell, quantity, rounding, verified/estimated/unavailable fee, and net-value tests in `backend/tests/unit/test_pricing_and_fees.py`
- [x] T020 [P] [US1] Add `POST /api/v1/analyses` contract tests for 200, 400, 422, and fee-unavailable responses in `backend/tests/contract/test_analyses.py`
- [ ] T021 [P] [US1] Add component tests for input validation, all waterfall stages, buy/sell sign labels, unavailable fees, and estimate/no-guarantee copy in `frontend/tests/components/analysis-flow.test.tsx`

### Implementation for User Story 1

- [ ] T022 [P] [US1] Implement supported contract transformations and complete lexicographic settlement-state/payoff enumeration in `backend/src/parity/domain/settlement.py`
- [ ] T023 [P] [US1] Implement tetrachoric pair fitting, bounded Higham/Dykstra correlation repair, and deterministic SciPy rectangle probabilities in `backend/src/parity/domain/correlation.py`
- [ ] T024 [P] [US1] Implement effective-dated fee evidence resolution and decimal-safe formula/rounding boundaries in `backend/src/parity/domain/fees.py`
- [ ] T025 [US1] Implement independence expectation, correlation-adjusted expectation, user-side quote difference, quantity scaling, and net expected value in `backend/src/parity/domain/pricing.py` using T022–T024
- [x] T026 [US1] Implement request-local waterfall orchestration with explicit unsupported/unavailable states in `backend/src/parity/services/analysis.py`
- [x] T027 [US1] Expose the stateless analysis endpoint without request IDs or persistence in `backend/src/parity/api/routes/analyses.py` and register it in `backend/src/parity/api/app.py`
- [ ] T028 [P] [US1] Implement the typed combo/quote input form and client-side shape feedback in `frontend/src/components/AnalysisForm.tsx`
- [ ] T029 [P] [US1] Implement the waterfall, fee-state, unit, rounding, and user-side quote display in `frontend/src/components/PriceWaterfall.tsx`
- [ ] T030 [US1] Connect the analysis page to the typed client and render sanitized API failures in `frontend/src/app/page.tsx`
- [ ] T031 [US1] Add the end-to-end canonical quote journey across FastAPI and Next.js in `frontend/tests/e2e/core-waterfall.spec.ts`

**Checkpoint**: User Story 1 is a complete demoable MVP and can be tested without User Stories 2–4.

---

## Phase 4: User Story 2 — Understand the Estimate (Priority: P2)

**Goal**: Explain every input, estimate, adjustment, fee status, source, and limitation without presenting
the model as objective truth.

**Independent Test**: Render one live-shaped response and one simulated response and verify their sources,
observation times, model/configuration versions, classifications, matrix repair, fee evidence, and limitations.

### Tests for User Story 2

- [ ] T032 [P] [US2] Add content-hash, deterministic-manifest, tamper-detection, and public-data-only tests in `backend/tests/unit/test_provenance.py`
- [ ] T033 [P] [US2] Add HTTPS host-allowlist, redirect-hop validation, timeout, mixed-time input, and no-secret-header tests in `backend/tests/unit/test_public_data.py`
- [ ] T034 [P] [US2] Add response tests proving correlation transformations, matrix repair diagnostics, source classifications, model/configuration versions, and fee evidence are complete in `backend/tests/contract/test_provenance.py`
- [ ] T035 [P] [US2] Add UI tests for provenance, observed/estimated/simulated labels, copula limitations, fee uncertainty, and provider-retention disclosure in `frontend/tests/components/analysis-details.test.tsx`

### Implementation for User Story 2

- [ ] T036 [P] [US2] Implement SHA-256 helpers and deterministic manifests restricted to public market data, public fee evidence, and committed fixtures in `backend/src/parity/data/provenance.py`
- [ ] T037 [P] [US2] Implement the minimal HTTPS allowlisted public-data client with every redirect revalidated in `backend/src/parity/services/public_data.py`
- [ ] T038 [US2] Attach ordered provenance, outcome transformations, matrix diagnostics, limitations, and reproducible model/configuration hashes in `backend/src/parity/services/analysis.py`
- [ ] T039 [P] [US2] Implement estimate, provenance, correlation-detail, fee-evidence, and privacy disclosure views in `frontend/src/components/AnalysisDetails.tsx`
- [ ] T040 [US2] Integrate expandable analysis details without recalculating backend values in `frontend/src/app/page.tsx`

**Checkpoint**: User Stories 1 and 2 independently distinguish observations, model estimates, simulations,
adjustments, unavailable values, and provider-level privacy limitations.

---

## Phase 5: User Story 3 — Reliable Demo Without Live Data (Priority: P3)

**Goal**: Run the complete analysis offline from a versioned deterministic scenario, with no silent fallback
and no persistent user data.

**Independent Test**: Block sockets, request `canonical-v1`, repeat ten times, and verify identical normalized
responses, visible simulated labels, no repository writes, and no browser restoration after reload.

### Tests for User Story 3

- [ ] T041 [P] [US3] Add canonical request/response fixture validation and ten-run deterministic serialization tests in `backend/tests/integration/test_deterministic_demo.py`
- [ ] T042 [P] [US3] Add socket-blocked, no-repository-write, no-database, and no-analysis-cache release gates in `backend/tests/integration/test_privacy_boundaries.py`
- [ ] T043 [P] [US3] Add live-dependency failure tests proving a sanitized 503 offers but never automatically substitutes `canonical-v1` in `backend/tests/contract/test_fallback.py`
- [ ] T044 [P] [US3] Add browser tests for explicit demo selection, simulated labels, empty cookies/storage/IndexedDB, clean URLs, reload clearing, and back-forward restoration in `frontend/tests/e2e/offline-privacy.spec.ts`

### Implementation for User Story 3

- [x] T045 [P] [US3] Create safe public canonical inputs, fixed timestamps, expected outputs, and provenance in `contracts/fixtures/canonical-v1.request.json`, `contracts/fixtures/canonical-v1.response.json`, and `backend/src/parity/fixtures/canonical-v1.json`
- [ ] T046 [P] [US3] Create a live-shaped response fixture containing no credentials, private data, or user-submitted values in `contracts/fixtures/live-shaped-v1.response.json`
- [ ] T047 [US3] Implement versioned fixture loading, hash verification, and explicit demo-mode orchestration in `backend/src/parity/services/demo.py` and `backend/src/parity/services/analysis.py`
- [x] T048 [US3] Implement sanitized live-failure responses that offer a new explicit demo request in `backend/src/parity/api/routes/analyses.py`
- [ ] T049 [P] [US3] Add the explicit Live/Deterministic Demo selector and fallback action in `frontend/src/components/DataModeSelector.tsx`
- [ ] T050 [US3] Keep analysis state only in React memory and clear it on reload/page restoration in `frontend/src/app/page.tsx`

**Checkpoint**: The full waterfall demo works without network access and creates no retrievable analysis history.

---

## Phase 6: User Story 4 — Review Historical Model Evidence (Priority: P4)

**Goal**: Show concise, leakage-resistant historical model evidence without implying future accuracy or profit.

**Independent Test**: Load the fixed validation fixture and verify strict observation/label availability,
walk-forward windows, embargo handling, sample counts, appropriate metrics, and insufficient-evidence behavior.

### Tests for User Story 4

- [ ] T051 [P] [US4] Add chronological split, label-availability, overlapping-window embargo, and rolling-origin fold tests in `backend/tests/unit/test_validation_splits.py`
- [ ] T052 [P] [US4] Add future-observation and future-label mutation tests proving earlier fits and valuations do not change in `backend/tests/unit/test_validation_leakage.py`
- [ ] T053 [P] [US4] Add hand-calculated Brier, MAE, RMSE, coverage, exclusion, and insufficient-evidence tests in `backend/tests/unit/test_validation_metrics.py`
- [ ] T054 [P] [US4] Add validation-summary rendering and historical-results-no-guarantee tests in `frontend/tests/components/validation-summary.test.tsx`

### Implementation for User Story 4

- [ ] T055 [US4] Implement timestamp-based walk-forward folds, label availability, embargoes, metrics, and insufficient-evidence gates in `backend/src/parity/domain/validation.py`
- [ ] T056 [US4] Attach a versioned validation summary without changing current-analysis estimates in `backend/src/parity/services/analysis.py`
- [ ] T057 [P] [US4] Implement the concise validation evidence panel and no-guarantee disclosure in `frontend/src/components/ValidationSummary.tsx`
- [ ] T058 [US4] Integrate the optional validation summary into `frontend/src/app/page.tsx`

**Checkpoint**: All four user stories are independently testable; historical evidence cannot access future data.

---

## Phase 7: Polish and Cross-Cutting Release Gates

**Purpose**: Verify the complete public-repository demo without expanding product scope.

- [ ] T059 [P] Verify the current official Kalshi fee schedule, RFQ role mapping, effective scope, exclusions, rounding treatment, source URL, retrieval/effective times, and content hash; record only public evidence in `backend/src/parity/fixtures/fees/` and mark unresolved details unavailable
- [ ] T060 [P] Add `.env.example` containing names and descriptions only for any optional public-data configuration, and re-audit `.gitignore` for credentials, private data, logs, databases, caches, and generated local artifacts
- [ ] T061 [P] Add dependency and source attribution required for the public repository in `README.md` and `THIRD_PARTY_NOTICES.md` without copying SnapCast code or representing its proprietary source as a Parity dependency
- [ ] T062 Run backend Ruff, mypy, pytest, OpenAPI export/drift, deterministic-repeatability, leakage, fee, and privacy gates from `specs/001-price-waterfall/quickstart.md`
- [ ] T063 Run frontend formatting, lint, typecheck, unit, contract, privacy E2E, and production-build gates from `specs/001-price-waterfall/quickstart.md`
- [ ] T064 Execute the complete offline demo and one live-failure recovery walkthrough; record only non-sensitive verification results in `README.md`
- [ ] T065 Audit all user-facing copy for estimate framing, simulated/observed labels, quote-premium wording, fee uncertainty, historical limitations, and absence of guaranteed-profit claims across `frontend/src/`
- [ ] T066 Audit the Git diff and tracked files for secrets, `.env` content, credentials, private datasets, user inputs, generated databases, logs, and accidental SnapCast source before any commit or push

---

## Dependencies and Execution Order

### Phase dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 and blocks every user story.
- **US1 (Phase 3)**: Depends on Phase 2 and is the MVP critical path.
- **US2 (Phase 4)**: Depends on the US1 response/service boundary; its tests and UI component can begin once Phase 2 is complete using contract fixtures.
- **US3 (Phase 5)**: Depends on the US1 analysis path; fixture creation and browser test scaffolding can begin after Phase 2.
- **US4 (Phase 6)**: Depends on the correlation/model-version boundary, but not on US2 or US3 UI completion.
- **Release gates (Phase 7)**: Depend on the stories selected for the demo; T066 is always last before commit/push.

### Within-story rules

1. Write the story's tests and verify the intended failures.
2. Implement pure domain functions before orchestration or API routes.
3. Keep FastAPI as the only quantitative authority; frontend tasks render typed responses only.
4. Regenerate and check OpenAPI/types after any schema change.
5. Complete the story checkpoint before calling the story done.

### Critical dependency chain

`T001 → T005 → T006–T009 → T013–T016 → T017–T027 → T030–T031`

This chain produces the core end-to-end MVP. T028–T029 can run alongside backend quantitative work after
T014–T016 establish the contract.

## Two-Developer Parallel Strategy

After both developers complete Setup and Foundational work:

- **Backend/modeling track**: T017–T027, then T032–T038, T041–T048, and T051–T056.
- **Frontend/integration track**: T021, T028–T031, then T035, T039–T040, T044, T049–T050, and T054, T057–T058.
- **Shared review points**: T016 contract agreement, US1 checkpoint, deterministic fixture approval at T045,
  and all Phase 7 release gates.

The frontend track uses the approved OpenAPI contract and committed fixtures while backend calculations are
implemented. Neither developer changes contract semantics without the other's review.

## Delivery Strategy

### MVP first

1. Complete Phases 1 and 2.
2. Complete US1 and its checkpoint.
3. If time is constrained, add US3 next so the demo is reliable offline.
4. Add US2 explainability, then US4 historical evidence.
5. Run the applicable Phase 7 gates before presenting or merging.

### Scope-control rule

Defer any task that does not improve the core waterfall's correctness, explainability, privacy, or demo
reliability. Do not introduce accounts, trade execution, databases, stored analysis history, analytics,
generic workflow infrastructure, or copied SnapCast implementation code.
