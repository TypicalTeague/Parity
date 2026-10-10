# Phase 0 Research: RFQ Combo Price Waterfall

## Settlement-aware probability model

**Decision**: Normalize each supported leg to a binary settlement-success indicator only after applying
its threshold/event condition, direction, observation time, and settlement rule. Preserve the supplied
marginal probability with a latent-normal threshold and describe the result as a Gaussian-copula
latent-threshold estimate.

**Rationale**: The model then represents contract settlement rather than raw market-price co-movement.
It also gives YES/NO and above/below legs one explicit transformation path.

**Alternatives considered**: Raw price correlation and raw-underlying correlation were rejected because
they ignore contract thresholds and settlement direction. Treating binary Pearson correlation directly
as latent Gaussian correlation was rejected because it is generally on the wrong scale.

## Dependence estimation

**Decision**: Align observations to a common time basis, use complete rows for the selected legs, map
each row to settlement outcomes, and estimate pairwise tetrachoric latent correlations by solving the
bivariate-normal threshold equation with SciPy's deterministic bracketed root solver. Degenerate margins,
insufficient samples, and boundary-only solutions are unavailable rather than silently smoothed.

**Rationale**: Tetrachoric correlation targets the latent-normal scale used by the copula. A common
complete-case window makes observation counts and matrix inputs auditable.

**Alternatives considered**: Pairwise deletion was rejected because different sample windows can amplify
matrix incoherence. Pseudocounts were rejected as an arbitrary hidden prior. Rank correlation of raw
outcomes does not meet the settlement-mapping requirement.

## Payoff valuation

**Decision**: Enumerate every joint binary settlement state (at most 16). Under independence, multiply
the applicable marginal success/failure probabilities for each state. Under dependence, obtain each
state's Gaussian rectangle probability. Apply the declared state-payoff table to both distributions.
Expose the product of leg probabilities specifically for an all-legs-win unit conjunction; otherwise
expose independent expected payoff, not a probability product.

**Rationale**: State enumeration is small, deterministic, inspectable, and supports conjunctions plus a
bounded documented subset of OR, XOR, and weighted payoffs through one engine.

**Alternatives considered**: Payoff-specific formulas were rejected as harder to audit and extend.
Blind multiplication was rejected because it misprices non-conjunction payoffs.

## Correlation coherence

**Decision**: Reject malformed matrices. For an otherwise valid matrix that is only slightly indefinite,
use Higham's nearest-correlation alternating projection with Dykstra correction. Accept a repair only when
it converges within versioned tolerances and stays below a versioned maximum-change threshold. Return the
original and used matrices plus convergence, eigenvalue, norm, and maximum-change metadata. Reject larger
repairs.

**Rationale**: Pairwise estimates need not form a positive-semidefinite multivariate matrix. A bounded,
disclosed nearest-correlation repair is safer than silently passing an incoherent structure downstream.

**Alternatives considered**: Silent eigenvalue clipping was rejected because it may not preserve a unit
diagonal or yield the nearest correlation matrix. Unconditional repair was rejected because it can
materially rewrite the evidence.

## Numerical reproducibility

**Decision**: Use SciPy multivariate-normal rectangle probabilities with fixed integration limits,
`maxpts`, absolute/relative tolerances, lexicographic state order, and a newly constructed fixed-seed NumPy
generator per analysis. Pin NumPy/SciPy versions and include integration configuration in the model version.
Handle marginal probabilities of zero or one analytically. Only tolerance-sized negative probabilities
or sum residuals may be corrected, and every correction is reported; larger residuals fail the estimate.

**Rationale**: This meets the three-second target without unseeded numerical drift and makes repeated
serialization stable within the pinned runtime/model version.

**Alternatives considered**: Unseeded integration and plain Monte Carlo were rejected for repeatability.
Fully nested deterministic quadrature was rejected as unnecessary delivery/performance risk for 16
four-dimensional rectangles.

## SnapCast reference reuse assessment

**Decision**: Use SnapCast as a design reference, not as a code dependency or source of verbatim code.
Its proprietary license does not grant Parity permission to copy, modify, or publish its implementation.
Parity will independently implement the selected general techniques against this specification and its
financial-domain tests. SnapCast remains read-only, and its existing uncommitted files are outside Parity's
work scope.

| Reusable concept or component | SnapCast source location | Proposed Parity destination | Classification | Required changes and risks |
|---|---|---|---|---|
| Correlation-matrix validation and positive-semidefinite repair | `src/nfl_projection/slips/copula.py` | `backend/src/parity/domain/correlation.py` | Rewrite | Implement the planned bounded Higham/Dykstra algorithm rather than copying eigenvalue clipping; expose repair diagnostics and reject material changes. |
| Seeded correlated-normal sampling | `src/nfl_projection/slips/copula.py` | `backend/src/parity/domain/correlation.py` and focused tests | Adapt | Recreate the deterministic RNG pattern only for simulation diagnostics or test oracles. It is not the primary valuation path and must not inherit sports pair classes. |
| Monte Carlo standard-error reporting | `src/nfl_projection/slips/payouts.py` and `src/nfl_projection/slips/copula.py` | Optional diagnostic in `backend/src/parity/domain/validation.py` | Adapt conditionally | Use only if a simulation-based diagnostic is retained. Report seed, draw count, and standard error; do not add a second production estimator solely for reuse. |
| Joint-outcome decomposition and expected-value calculation | `src/nfl_projection/slips/copula.py`, `src/nfl_projection/slips/payouts.py` | `backend/src/parity/domain/settlement.py` and `backend/src/parity/domain/pricing.py` | Rewrite | Enumerate every supported financial settlement state and apply its payoff. Do not reuse all-hit parlay or PrizePicks payout semantics. |
| Dependence fitting and held-out checking | `src/nfl_projection/slips/fit.py`, `src/nfl_projection/slips/copula.py` | `backend/src/parity/domain/correlation.py` and `backend/src/parity/domain/validation.py` | Rewrite | Replace NFL relationship classes and randomized-PIT sports residuals with timestamp-aligned financial outcomes, contract transformations, tetrachoric fitting, and walk-forward checks. Never assume cross-market independence. |
| Chronological splits and rolling-origin folds | `src/nfl_projection/evaluation/splits.py` | `backend/src/parity/domain/validation.py` | Adapt | Generalize season/week keys to UTC observation and label-availability timestamps; apply an embargo where windows overlap. |
| Future-data mutation leakage tests | `tests/leakage/test_no_leakage.py` | `backend/tests/unit/test_validation_leakage.py` | Adapt | Mutate observations and labels at or after a cutoff and prove earlier fits/valuations are byte-stable; use financial fixtures rather than player statistics. |
| Content-hash manifests and tamper detection | `src/nfl_projection/data_sources/manifests.py`, `tests/unit/test_manifest.py` | `backend/src/parity/data/provenance.py` and `backend/tests/unit/test_provenance.py` | Adapt | Restrict manifests to public market data, deterministic fixtures, and public fee evidence. Never manifest user requests, quotes, results, credentials, or private data. |
| HTTPS host allowlist and redirect revalidation | `src/nfl_projection/data_sources/network.py` | `backend/src/parity/services/public_data.py` | Adapt | Replace NFL hosts with the minimum verified Kalshi/public-data hosts and test every redirect hop. Keep the offline fixture path independent of network access. |
| Construction-time Pydantic invariants and forbidden extras | `src/nfl_projection/domain/prediction.py` | `backend/src/parity/schemas/analysis.py` | Adapt | Replace sports fields with classified values, settlement/payoff structures, fee status, provenance, and model/config versions; retain timezone and cross-field validation. |
| Verified, hashed configuration evidence | `src/nfl_projection/slips/payouts.py` | `backend/src/parity/domain/fees.py` and `backend/src/parity/fixtures/fees/` | Adapt | Preserve verification status, source date, and hash concepts, but implement only current official Kalshi rules and fail closed on uncertain scope or RFQ role. |
| Network-blocked and no-repository-write release gates | `tests/unit/test_slips_no_network.py` | `backend/tests/integration/test_privacy_boundaries.py` | Adapt | Assert deterministic mode opens no sockets and analysis requests create no repository files, cache entries, logs, or history. Public-data refresh tests remain isolated. |
| SQLite/history/run stores and write-once user outputs | `src/nfl_projection/slips/stores.py`, `src/nfl_projection/slips/history.py`, `src/nfl_projection/slips/records.py` | None | Reject | Persistence of submitted analyses conflicts with Zero Data and adds no hackathon-demo value. |
| NFL pair taxonomy, different-game independence, sports feature engineering, and PrizePicks rules | `src/nfl_projection/slips/legs.py`, `src/nfl_projection/features/`, `src/nfl_projection/slips/payouts.py` | None | Reject | These encode a different domain and could produce materially wrong financial dependence, settlement, or fee results. |
| Python 3.12 quality-tool configuration | `pyproject.toml` | `backend/pyproject.toml` | Adapt | Retain pytest, Hypothesis, Ruff, mypy, NumPy, Pandas, SciPy, and Pydantic patterns; add FastAPI/HTTPX/Uvicorn and exclude unrelated sports/model dependencies. |

**Rationale**: The reference project provides tested patterns for reproducibility, leakage resistance,
provenance, and defensive validation. A clean-room financial implementation captures those benefits without
publishing proprietary code or importing NFL assumptions, persistent history, or unnecessary infrastructure.

**Alternatives considered**: Copying modules directly was rejected because of licensing and domain mismatch.
Adding SnapCast as a package dependency was rejected because it would couple Parity to private sports code.
Ignoring the reference entirely was rejected because its validated patterns reduce design and testing risk.

## Specification clarification determination

**Decision**: No change to the approved feature specification is required before implementation planning
continues. FR-006 through FR-010 already require settlement-aware payoff valuation, transformation of
historical underlying outcomes through contract rules, and disclosed dependence repair. FR-017, FR-021,
FR-024, and the Zero Data requirements already cover provenance, look-ahead prevention, reproducibility,
and non-persistence.

The plan records three implementation interpretations without changing product scope:

1. A leg may be represented by a binary success indicator only after applying its supported settlement
   rule; the combo itself may have multiple settlement states and non-binary payoffs through its complete
   state-payoff table.
2. SnapCast's assumption that different games are independent does not transfer. Parity estimates or
   explicitly marks unavailable every dependence relationship required by the selected combo.
3. Deterministic rectangle integration remains the primary estimator. A Monte Carlo path, if used at all,
   is a labeled validation diagnostic with an explicit seed, draw count, and standard error.

**Revisit trigger**: Amend the specification before implementation only if the team wants legs whose
settlement cannot be reduced to the currently supported success/failure state representation, or wants
simulation uncertainty to become a user-visible product requirement rather than validation metadata.

## Fee policy and verification

**Decision**: Model fees as effective-dated policy evidence, never as a global constant. Resolution order
is event override, then series fee-change metadata, then the canonical published schedule. Store source
URL, retrieval and effective times, content hash and HTTP metadata, evidence location, scope/exclusions,
fee type/multiplier, parser version, and verification status. If effective scope, an exception, or the
RFQ participant's fee role cannot be verified, return `unavailable` (or an explicitly labeled estimate)
and keep fee-adjusted net value unavailable.

**Rationale**: Kalshi schedules fee changes and combo exceptions. Current official documentation supports
requester/taker treatment, but quoter/maker mapping may still require fill or exchange-metadata evidence.
Failing closed prevents an unverified constant from appearing authoritative.

**Alternatives considered**: Hard-coded maker/taker percentages, assuming zero fees, and extending a combo
schedule to excluded products were rejected.

**Verified source snapshot at planning time (2026-10-10)**: The official fee schedule retrieved during
research was effective 2026-07-07 and stated taker `ceil6(M × 0.07 × C × P × (1-P))` and maker
`ceil6(M × 0.0175 × C × P × (1-P))`; its non-standard table listed KXMVE combos excluding uncorrelated NFL
combos with taker multiplier 1 and maker multiplier 2. Production use still requires a fresh live-policy
check and the exchange's separate balance-rounding treatment; this planning snapshot is not a runtime
authority.

**Primary sources**:

- [Kalshi fee schedule](https://kalshi.com/docs/kalshi-fee-schedule.pdf)
- [Kalshi regulatory fee-schedule page](https://kalshi.com/regulatory/fee-schedule)
- [Kalshi RFQ documentation](https://docs.kalshi.com/getting_started/rfqs)
- [Kalshi fee rounding](https://docs.kalshi.com/getting_started/fee_rounding)
- [Series fee changes](https://docs.kalshi.com/api-reference/exchange/get-series-fee-changes)
- [Event fee changes](https://docs.kalshi.com/api-reference/events/get-event-fee-changes)

## Stateless API and privacy boundary

**Decision**: Compute in request-local memory through `POST /api/v1/analyses`. Do not create analysis IDs,
users, sessions, databases, queues, or history. Logs are allowlisted to fixed route/operation, status,
duration, model version, and non-user-derived error code. Sanitize validation errors and suppress input
values. Return `Cache-Control: no-store, private, max-age=0, must-revalidate`, `Pragma: no-cache`, and
`Expires: 0` on success and error. Keep browser state only in React memory and clear it on page lifecycle
restoration; use no storage, cookies, analytics, service worker, or payload-retaining proxy.

**Rationale**: This directly enforces the product's zero-data requirements while retaining enough aggregate
operational metadata to debug availability.

**Alternatives considered**: Request IDs, server sessions, and persisted client stores were rejected as
unnecessary correlation/retention surfaces. Financial inputs in GET query parameters were rejected because
URLs are commonly retained outside application control.

## Contract and frontend type safety

**Decision**: Pydantic/FastAPI is the executable schema source. Export and commit OpenAPI, generate strict
TypeScript types with `openapi-typescript`, and call it through `openapi-fetch`. Return the complete
waterfall, provenance, model metadata, fallback state, and disclosures in one response. Use discriminated
unions for availability and fee status; decimal strings at currency boundaries; bounded JSON numbers for
statistical probabilities; UTC ISO-8601 timestamps.

**Rationale**: One contract prevents frontend/backend unit and nullability drift while keeping calculations
out of the browser.

**Alternatives considered**: Handwritten parallel TypeScript models were rejected as a second authority.
Adding a second runtime schema library was deferred because it duplicates Pydantic for this scope.

## Deterministic fallback and historical validation

**Decision**: Commit versioned canonical request/response fixtures with fixed timestamps, model version,
correlation/integration settings, fee evidence, ordering, rounding, classifications, and disclosures. Live
failure offers this scenario explicitly and never substitutes it silently. Historical validation uses
strict walk-forward fitting: only records and final labels available before evaluation time are eligible;
overlapping windows use a configured embargo. Report Brier score for unit-binary payoffs and MAE/RMSE for
general bounded payoffs, plus fit/evaluation windows, counts, coverage, exclusions, and limitations.

**Rationale**: A committed result is both an offline demo and an integration contract. Walk-forward fitting
prevents look-ahead bias and makes insufficient evidence visible.

**Alternatives considered**: Test-time-generated fixtures, random splits, full-sample fitting, and silently
switching to simulated inputs were rejected because they weaken reproducibility, validation integrity, or
provenance.

## Tooling and dependency scope

**Decision**: Use only the constitution's runtime stack plus Uvicorn and small contract/client tooling.
Backend quality tools are pytest, HTTPX, Ruff, and mypy. Frontend quality tools are TypeScript, ESLint,
Prettier, Vitest, Testing Library, and one Playwright Chromium suite. Do not add a database, auth framework,
analytics SDK, error-reporting SDK, scikit-learn, or generic workflow infrastructure.

**Rationale**: NumPy/SciPy/Pandas already cover the statistical work; the selected tools give fast feedback
on the highest-risk quantitative, contract, rendering, and privacy boundaries.

**Alternatives considered**: A single Next.js full-stack application conflicts with backend quantitative
ownership. Additional infrastructure and modeling libraries do not reduce delivery risk for this demo.
