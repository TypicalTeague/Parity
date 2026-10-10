# Parity

Parity is a quantitative pricing analytics prototype for evaluating Request for Quote (RFQ) combo markets. It presents a four-part price waterfall:

1. an independence baseline;
2. a Gaussian-copula correlation adjustment;
3. the difference between model-estimated fair value and the quoted price; and
4. applicable execution fees and fee-adjusted net expected value, when supported by verified fee evidence.

Parity estimates fair value. It does not establish objectively correct probabilities, guarantee profits, or characterize quote differences as guaranteed market-maker profits. The project does not execute trades.

## Current status

The repository contains a working, stateless backend skeleton and a frontend integration foundation. The current end-to-end analysis uses the versioned `canonical-v1` deterministic demo fixture.

Implemented and tested:

- FastAPI health and analysis endpoints;
- strict Pydantic request and response validation;
- independence expectations and settlement-state enumeration;
- all-legs-win, OR, XOR, and explicit non-binary state-table payoffs;
- Gaussian-copula joint-state probabilities using SciPy;
- bounded correlation-matrix repair diagnostics;
- buy/sell quote comparisons;
- deterministic fixtures and byte-stable responses;
- sanitized errors and no-store response headers;
- generated OpenAPI and TypeScript API types.

Still in progress:

- live public-market data ingestion;
- transformation of real contract thresholds and settlement definitions;
- dependence fitting from time-aligned historical financial outcomes;
- verified, effective-dated Kalshi fee evidence and fee-adjusted net value;
- walk-forward historical validation and look-ahead-bias gates;
- the complete user interface and end-to-end browser tests.

The calculations are real and tested, but the current end-to-end inputs and correlation matrix are simulated. Simulated and unavailable values are explicitly labeled.

## Repository structure

```text
backend/                      FastAPI application and quantitative domain code
contracts/                    Generated OpenAPI contract and safe demo fixtures
frontend/                     Next.js application and generated API client types
specs/001-price-waterfall/    Specification, plan, research, data model, and tasks
.specify/                     GitHub Spec Kit support files
```

The project follows GitHub Spec Kit's sequence: constitution, specification, plan, tasks, then implementation. The active implementation checklist is in [`specs/001-price-waterfall/tasks.md`](specs/001-price-waterfall/tasks.md).

## Prerequisites

- Python 3.12 or newer
- Node.js 20.9 or newer
- npm

No Kalshi credentials are required for the deterministic demo.

## Backend setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e "./backend[dev]"
uvicorn parity.api.app:app --app-dir backend/src --reload
```

The API runs at `http://127.0.0.1:8000` by default. Useful routes:

- `GET /api/v1/health`
- `POST /api/v1/analyses`
- `GET /docs`

Submit the committed deterministic scenario from another terminal:

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  --data @contracts/fixtures/canonical-v1.request.json \
  http://127.0.0.1:8000/api/v1/analyses
```

Live mode currently fails closed with a sanitized `503` response and offers the deterministic scenario as an explicit fallback. It never silently substitutes simulated data.

## Frontend setup

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

The frontend should consume the generated types in `frontend/src/lib/api/generated.ts` and use FastAPI as the sole authority for quantitative calculations. To regenerate types after an intentional API-contract change:

```bash
npm --prefix frontend run generate:api
```

Coordinate contract changes with both developers and commit the regenerated OpenAPI document, TypeScript types, and canonical fixtures together.

## Tests and quality checks

With the Python environment active and frontend dependencies installed:

```bash
make backend-check
make frontend-check
make contracts-check
```

Or run the current backend suite directly:

```bash
python -m pytest backend/tests
```

See [`specs/001-price-waterfall/quickstart.md`](specs/001-price-waterfall/quickstart.md) for the planned complete validation and privacy gates. Some checks described there correspond to tasks that are not yet implemented.

## Privacy and public-repository rules

Parity follows a Zero Data design: no accounts, user profiles, databases, uploaded-file storage, saved analysis history, or sensitive request logging. Do not commit credentials, `.env` files, tokens, private datasets, user-generated data, logs, or local databases. The repository's `.gitignore` excludes common sensitive and local artifacts.

Use public market data where practical and clearly identify observed, estimated, adjusted, simulated, and unavailable values. Fee rules must include verified public evidence and dates rather than unsupported hardcoded assumptions.

## Working together

Frontend work can proceed against the committed OpenAPI contract, generated TypeScript types, and canonical fixtures while backend modeling continues. Keep calculations in the backend, render the typed response in the frontend, and coordinate before changing request or response schemas.

## License

A project license has not yet been selected. Until one is added, copyright law reserves reuse rights by default.
