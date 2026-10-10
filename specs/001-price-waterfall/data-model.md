# Data Model: RFQ Combo Price Waterfall

The model describes request-local domain values and versioned public fixtures. It does not imply a
database. No user, session, analysis-history, or persistent result entity exists.

## Shared value types

### Classified value

- `value`: bounded JSON number for probabilities/statistical deltas, or canonical decimal string for money
- `unit`: `probability`, `usd_per_contract`, `usd_total`, or another contract-defined unit
- `classification`: `observed`, `model_estimated`, `simulated`, `user_provided`, `adjusted`, or `unavailable`
- `precision`: displayed decimal places and rounding mode
- `available`: boolean; when false, `value` is absent and `reason_code` is required

### Provenance reference

- `source_id`, `source_name`, `source_kind`, `source_url` (public fixed URL only)
- `observed_at`, `retrieved_at`, `effective_at`: timezone-aware UTC timestamps as applicable
- `classification`: shared classification enum
- `fixture_version`, `content_sha256`, `fallback_used`: as applicable
- `limitations`: stable non-user-derived descriptions

Validation: timestamps include offsets; no source URL may contain submitted financial inputs; simulated and
fallback-derived values must carry a fixture version; unavailable values must identify why.

## Contract Leg

Represents one settlement-aware component of a combo.

- `leg_id`: request-local opaque label, unique within the request and safe for error paths
- `market_ticker`: public market identifier
- `underlying_outcome`: public outcome identifier/name
- `position`: `yes` or `no`
- `condition`: discriminated union such as threshold-above, threshold-below, or named-event outcome
- `settlement_rule`: versioned supported-rule identifier and plain-language summary
- `payoff_contribution`: decimal string in the combo payoff unit
- `probability`: bounded classified value in `[0,1]`
- `observation_time`: UTC timestamp
- `source`: provenance reference

Validation: exactly two to four unique legs per combo; no duplicate or contradictory positions; aligned
observation times under the selected policy; supported condition/settlement combination; probability present,
fresh, and bounded. A boundary probability of zero or one is valid and handled analytically.

Relationships: belongs to one `Combo Definition`; historical observations are transformed through this leg's
condition and settlement rule before entering a `Correlation Estimate`.

## Combo Definition

- `combo_id`: optional public combo/RFQ identifier; never a generated analysis identifier
- `legs`: ordered list of 2–4 contract legs
- `payoff_rule`: `all_legs_win`, `any_leg_wins`, `exactly_one_wins`, or explicit supported state-payoff table
- `state_payoffs`: for general supported structures, a complete mapping from binary leg-state tuple to a
  decimal-string payoff
- `currency`: ISO currency code, initially `USD`
- `payout_unit`: per-contract payoff unit

Validation: every one of the `2^n` states is represented exactly once for a state table; payoffs are bounded,
non-negative, decimal-safe, and expressed in one unit; rule and table agree; unsupported or logically
contradictory structures return `UNSUPPORTED_COMBO` without valuation.

## RFQ Quote

- `intended_side`: `buy` or `sell`, always from the user's perspective
- `participant_role`: `requester`, `quoter`, or `unknown`
- `price_per_contract`: canonical non-negative decimal string in USD
- `quantity`: positive integer
- `observation_time`: UTC timestamp
- `source`: user-provided provenance reference

Validation: side and quantity required; quoted amount within the payoff's valid economic bounds; units explicit;
no quote or amount is placed in a URL, identifier, or log field.

## Market Input Set

- `leg_probabilities`: one probability per leg with provenance/freshness
- `historical_observations`: public time-indexed outcome rows or a reference to a versioned public fixture
- `alignment_policy`: common timestamp and complete-case rules
- `freshness_policy`: versioned maximum ages
- `data_mode`: `live` or `deterministic_demo`
- `fixture_version`: required only in demo mode

Validation: no mixture of incompatible observation times; live and simulated values cannot be silently combined;
public-data cache keys contain only market and observation metadata, never a user/session/request key.

## Correlation Estimate

- `method`: versioned tetrachoric/Gaussian-copula method identifier
- `historical_window_start`, `historical_window_end`
- `observation_count`, `rows_removed`, `missing_data_treatment`
- `outcome_transformations`: settlement mapping per leg
- `original_matrix`, `used_matrix`: ordered square decimal arrays
- `adjustment`: absent, or method, tolerances, iterations, convergence, minimum eigenvalues, Frobenius norm,
  maximum entry change, threshold, and accepted status
- `integration`: seed, state order, `maxpts`, absolute/relative tolerances, residual and correction metadata
- `limitations`: discrete-margin and data-quality disclosures

Validation: dimensions match ordered legs; finite symmetric values, unit diagonal, entries in `[-1,1]`; used matrix
is PSD within tolerance; any repair is bounded and disclosed. Degenerate, insufficient, non-convergent, or materially
incoherent inputs make the adjusted estimate unavailable.

State transition: `raw` → `validated` → (`coherent` | `repair_candidate`) → (`accepted` | `rejected`). Only
`accepted` or directly `coherent` estimates may reach valuation.

## Fee Policy Evidence

- `policy_id`, `source_url`, `source_kind`
- `retrieved_at`, `effective_at`, optional `scheduled_at`
- `content_sha256`, optional `etag`, `last_modified`, `content_type`
- `scope`: exchange/series/event identifiers plus exclusions
- `fee_type`: `maker` or `taker`; `multiplier`; versioned formula identifier
- `rfq_role_mapping`: requester/quoter mapping and evidence level
- `parser_version`, `evidence_location`, `verification_status`

Validation: public official source; hash and effective time present; requested market/time/role is in verified scope;
event evidence takes precedence over series evidence, which takes precedence over canonical schedule evidence.

## Fee Assessment

- `status`: `verified`, `estimated`, or `unavailable`
- `policy`: fee policy evidence when available
- `fee_role`, `quantity`, `price_per_contract`
- `model_trade_fee`, `balance_rounding_fee`, `rebate`, `total_fee`: decimal USD strings when applicable
- `assumptions`, `unavailable_reason`: explicit stable descriptions

Validation: verified assessments must have verified applicable evidence and all formula inputs; estimated fees identify
the assumption; unavailable fees contain no authoritative amount. `total_fee` reconciles its components under the
published exchange rounding rule.

State transition: `unresolved` → (`verified` | `estimated` | `unavailable`). No implicit zero-fee transition exists.

## Waterfall Result

- `independence_baseline`: classified probability for unit conjunctions or expected payoff for general structures
- `correlation_adjustment`: adjusted minus independent value, same unit
- `model_fair_value`: correlation-adjusted expected payoff
- `quote_difference`: user-side economics relative to model value, with side/sign convention
- `fees`: fee assessment
- `net_expected_value`: quantity-scaled user-side quote difference less applicable fees, or unavailable
- `provenance`: ordered references for every input/result
- `observation_time`, `model_version`, `configuration_version`, `fallback_used`
- `disclosures`: estimate, copula limitation, fee status, historical-performance, privacy/provider disclosures

Validation: `model_fair_value = independence_baseline + correlation_adjustment` within the declared precision;
quote and net signs follow intended side; all monetary calculations cross a documented decimal boundary before
serialization; no rounded display value determines the sign; all displayed values have classification and unit.

## Validation Summary

- `status`: `available` or `insufficient_evidence`
- `model_version`, `payoff_kind`
- `fitting_window`, `evaluation_window`, optional `embargo`
- `eligible_count`, `excluded_count`, `prediction_count`, `coverage`
- `metrics`: Brier for unit binary payoff; MAE/RMSE for general bounded payoff
- `limitations`, `no_guarantee_disclosure`

Validation: for every prediction, training observations and final labels have `available_at < evaluation_time`;
minimum training and evaluation counts are versioned; unavailable metrics are omitted, never zero-filled.

State transition: `candidate` → `time_order_checked` → (`available` | `insufficient_evidence`).

## Privacy Disclosure

- `application_behavior`: no accounts, tracking, request/result persistence, or payload logging
- `public_cache_behavior`: market/observation keyed only
- `external_services`: service name, data received, necessity, and retention uncertainty
- `provider_retention`: accurate limitation for IP/request metadata outside application control
- `version`, `effective_at`

This content is versioned product copy, not user-specific data.
