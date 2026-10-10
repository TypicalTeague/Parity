# Quickstart Validation Guide: RFQ Combo Price Waterfall

This guide defines runnable validation once the planned backend/frontend skeleton exists. It does not
contain implementation code. The API shapes are in [contracts/openapi.yaml](contracts/openapi.yaml), and
domain invariants are in [data-model.md](data-model.md).

## Prerequisites

- Python 3.12+
- A supported Node.js release and npm
- Chromium installed through Playwright for browser privacy checks
- No Kalshi credentials are required for the canonical deterministic scenario

## Install and start

```bash
python -m pip install -e "./backend[dev]"
npm --prefix frontend ci
uvicorn parity.api.app:app --app-dir backend/src --reload
npm --prefix frontend run dev
```

Open the frontend URL printed by Next.js. The backend must expose only stateless fixed-route analysis and
health operations; do not place analysis inputs in the browser URL.

## Validate the canonical offline scenario

1. Disable network access to live market-data services or select **Deterministic demo** directly.
2. Load `canonical-v1` and submit it from the analysis page.
3. Confirm the result visibly shows the independence baseline, correlation adjustment, model fair value,
   user-side quote difference, fee status/amount, and net expected value.
4. Confirm every value displays a unit and one of the required classifications, and simulated values are
   unmistakable.
5. Confirm estimate/no-guarantee language, model/configuration version, fixed observation time, fixture
   version, fee evidence status, and `fallback_used` are visible.
6. Repeat ten times and compare normalized response bytes and displayed rounding; every run must match.

Expected outcome: the complete waterfall is available in under three seconds without a live dependency.
No live failure silently changes a submitted live analysis into a simulated one.

## Validate payoff and dependence behavior

Run the focused backend suite:

```bash
python -m pytest backend/tests/unit backend/tests/contract
```

The suite must demonstrate:

- all-legs-win independence equals the product of leg probabilities;
- OR, XOR, and supported state-table payoffs equal hand-enumerated independent expectations;
- identity correlation matches independence within declared numerical tolerance;
- threshold/direction reversals transform historical outcomes correctly;
- zero/one marginals are handled analytically;
- malformed or materially incoherent matrices fail, while a small accepted repair is fully disclosed;
- state probabilities remain bounded and sum to one within the correction policy;
- unsupported settlement/payoff structures return no fair value;
- identical pinned inputs produce identical serialized output.

## Validate fees and unavailable states

Use one fixture with verified effective-dated fee evidence and fixtures for expired evidence, excluded combo
scope, unknown RFQ role, and unavailable policy endpoints.

Expected outcomes:

- a verified fee cites the source, effective/retrieval times, scope, formula inputs, multiplier, exchange
  rounding components, and verification status;
- event overrides outrank series evidence, which outranks the canonical schedule;
- an unverified exception or role never silently becomes zero or a generic constant;
- fee-adjusted net value is unavailable when an authoritative fee cannot be computed;
- the gross quote comparison remains visible with a clear limitation.

## Validate live failure and fallback

Force the public data adapter to time out or return incomplete/mixed-time data, then request a live analysis.

Expected outcome: the API returns the documented sanitized dependency error or unavailable state and offers
`canonical-v1`. Only a new explicit demo request returns simulated results.

## Validate historical evidence

```bash
python -m pytest backend/tests -k "walk_forward or validation_summary"
```

Expected outcomes: future records cannot change an earlier prediction; data or labels available exactly at
the evaluation time are excluded; shuffled source order does not change results; Brier/MAE/RMSE fixtures
match hand calculations; insufficient samples produce `insufficient_evidence` and no invented metric.

## Validate privacy and cache behavior

Submit a recognizable sentinel string/value through success, validation failure, unsupported combo, live
dependency failure, and forced internal-error paths.

```bash
python -m pytest backend/tests -k "privacy or logging or cache"
npm --prefix frontend run test:e2e -- --grep "privacy|reload|storage|cache"
```

Expected outcomes:

- sentinel inputs and result values appear in no application/access logs or error reports;
- errors contain only sanitized field paths, codes, and corrective messages;
- success and error responses include `Cache-Control: no-store, private, max-age=0, must-revalidate`,
  `Pragma: no-cache`, and `Expires: 0`;
- cookies, local/session storage, and IndexedDB remain empty;
- no submitted value occurs in a requested URL, analytics request, or third-party request;
- reload, a new browser context, and back-forward restoration do not restore an analysis;
- public cache keys contain market/observation metadata only.

## Run the full quality gate

```bash
python -m ruff check backend
python -m ruff format --check backend
python -m mypy backend/src
python -m pytest backend/tests
python -m parity.tools.export_openapi --check contracts/openapi.json
npm --prefix frontend run generate:api
npm --prefix frontend run contract:check
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend test -- --run
npm --prefix frontend run test:e2e
npm --prefix frontend run build
```

Expected outcome: formatting, types, unit/integration/contract tests, OpenAPI drift checks, frontend rendering,
browser privacy tests, and production build all pass. Generated frontend types and committed response fixtures
must match the backend schema before dependent frontend changes are accepted.
