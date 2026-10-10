# Feature Specification: RFQ Combo Price Waterfall

**Feature Branch**: `spec/001-price-waterfall`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Estimate the fair value of a Kalshi RFQ combo and explain it through
an independence baseline, correlation adjustment, quote premium, and verified platform fees."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluate a Combo Quote (Priority: P1)

A retail trader defines or selects a supported RFQ combo, supplies the quoted terms, and receives a
four-part price waterfall showing the independent estimate, correlation-adjusted estimate, quote
difference, fees, and net expected value for the intended side of the trade.

**Why this priority**: This is Parity's core decision-support experience and provides a complete,
demonstrable outcome without any other feature.

**Independent Test**: Use a deterministic two-leg combo with known probabilities, settlement rules,
quote, quantity, correlation inputs, and fee rule. Confirm that all four stages and the final net
expected value are shown with correct signs, units, and labels.

**Acceptance Scenarios**:

1. **Given** a supported combo and complete deterministic inputs, **When** the trader requests an
   analysis, **Then** the trader sees all four waterfall stages and a net expected value for the
   selected side and quantity.
2. **Given** a conjunction whose legs are treated as independent, **When** the baseline is calculated,
   **Then** the displayed joint probability equals the product of the eligible leg probabilities.
3. **Given** a supported payoff that is not a simple all-legs-win binary conjunction, **When** the
   baseline is calculated, **Then** it reflects the stated settlement and payoff rules rather than
   blindly multiplying probabilities.
4. **Given** a market quote above or below the model estimate, **When** the comparison is displayed,
   **Then** the difference is described from the trader's selected side and is not characterized as
   guaranteed profit.

---

### User Story 2 - Understand the Estimate (Priority: P2)

A retail trader inspects the assumptions and provenance behind an analysis so they can understand
which values were observed, estimated, simulated, adjusted, or unavailable.

**Why this priority**: Quantitative output is useful only when the user can see its assumptions,
limitations, and relationship to the quoted market price.

**Independent Test**: Analyze one live-data-shaped fixture and one deterministic fixture. Confirm that
each result identifies its source class, observation time, relevant model assumptions, settlement
interpretation, fee status, and any fallback or mathematical adjustment.

**Acceptance Scenarios**:

1. **Given** an analysis using estimated correlations, **When** the trader opens its details, **Then**
   the trader sees the historical window, observation count, outcome mapping, and model limitation.
2. **Given** a correlation input that requires an adjustment to become mathematically usable,
   **When** an estimate is produced, **Then** the adjustment is disclosed rather than silently hidden.
3. **Given** a fee rule that cannot be verified, **When** the result is displayed, **Then** the fee
   and fee-adjusted net value are marked unavailable or estimated with the assumption identified.
4. **Given** any completed analysis, **When** the trader reviews it, **Then** model fair value is
   clearly labeled as an estimate rather than an objectively correct probability.

---

### User Story 3 - Complete a Reliable Demo Without Live Data (Priority: P3)

A presenter can demonstrate the full analysis when live public market data is unavailable, delayed,
incomplete, or incompatible with the selected combo.

**Why this priority**: External availability must not prevent a working hackathon demonstration.

**Independent Test**: Disable live-data access and run the canonical deterministic scenario. Confirm
that the entire waterfall remains usable, produces the documented result, and visibly labels all
fixture-derived values as simulated.

**Acceptance Scenarios**:

1. **Given** live data is unavailable, **When** the presenter selects the deterministic demo, **Then**
   the complete four-stage waterfall is produced without live-data dependencies.
2. **Given** deterministic demo mode is active, **When** results are shown, **Then** every simulated
   or estimated value is visibly labeled and cannot be mistaken for a current market observation.
3. **Given** the same deterministic inputs and configuration, **When** the analysis is repeated,
   **Then** all displayed values and classifications are identical.

---

### User Story 4 - Review Historical Model Evidence (Priority: P4)

A retail trader or judge can view a concise historical validation summary to understand how the
model behaved on time-ordered historical observations without treating past performance as a
guarantee.

**Why this priority**: Validation supports credibility, but it is secondary to producing and
explaining the current estimate.

**Independent Test**: Load a fixed historical validation result and confirm it identifies the fitting
window, evaluation window, sample size, selected error measures, and an explicit no-guarantee
disclosure.

**Acceptance Scenarios**:

1. **Given** a historical validation summary, **When** it is displayed, **Then** it shows that each
   evaluated prediction used only information available before its evaluation time.
2. **Given** insufficient historical observations, **When** validation is requested, **Then** the
   system reports insufficient evidence instead of presenting an unsupported performance result.
3. **Given** historical performance metrics, **When** the trader views them, **Then** the display
   states that historical fit does not guarantee future accuracy or profit.

### Edge Cases

- A leg probability is missing, outside the inclusive 0-to-1 range, stale, or associated with a
  different observation time than the remaining inputs.
- A combo has fewer than two legs, exceeds the supported four-leg demo scope, duplicates a leg, or
  contains contradictory positions.
- Contract thresholds overlap, reverse direction, or imply settlement relationships that make simple
  correlation assumptions invalid.
- A settlement rule or payoff structure cannot be represented by the supported model.
- Correlation inputs are missing, based on too few observations, outside their valid range, or form
  an incoherent dependence structure.
- The independence estimate or correlation-adjusted estimate is at or extremely near 0 or 1.
- A quote is absent, outside its valid price bounds, has zero or negative quantity, or is supplied
  without an intended trade side.
- Fees depend on information that is unavailable, or the current fee rule cannot be verified.
- Live data becomes unavailable partway through an analysis or contains a mixture of observation
  times.
- Rounding could reverse the displayed sign of a very small premium or net expected value.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST allow a user to analyze a combo containing two to four contract legs.
- **FR-002**: Each leg MUST identify the underlying outcome, position direction, threshold or event
  condition, settlement rule, payoff contribution, probability input, observation time, and source.
- **FR-003**: The product MUST accept RFQ terms sufficient to interpret the user's economics,
  including intended side, quoted amount or price, and quantity.
- **FR-004**: The product MUST validate completeness, units, ranges, timestamps, duplicated legs, and
  supported settlement/payoff structures before producing a value.
- **FR-005**: For a supported all-legs-win binary conjunction, the independence baseline MUST equal
  the product of individual leg probabilities.
- **FR-006**: For any other supported payoff structure, the independence baseline MUST use the stated
  settlement and payoff rules and MUST NOT be represented as a simple probability product.
- **FR-007**: The product MUST produce a correlation-adjusted joint estimate using a Gaussian-copula
  model for supported combos.
- **FR-008**: Correlation modeling MUST map historical underlying outcomes to each contract's
  threshold, direction, and settlement rule before estimating dependence.
- **FR-009**: The product MUST identify the historical window, observation count, missing-data
  treatment, and outcome transformation used for each correlation estimate.
- **FR-010**: The product MUST reject unusable dependence inputs or disclose any adjustment made to
  obtain a mathematically coherent estimate.
- **FR-011**: The waterfall MUST display the independence baseline, correlation adjustment, resulting
  model fair value, quote difference, applicable fees, and net expected value as distinct values.
- **FR-012**: Quote differences MUST be expressed from the user's intended side with explicit units
  and MUST NOT be labeled as guaranteed profit or guaranteed market-maker profit.
- **FR-013**: Fee results MUST identify the applicable verified rule, its effective date or retrieval
  time, the inputs used, and whether the result is verified, estimated, or unavailable.
- **FR-014**: The product MUST NOT use an unverified fee constant as though it were authoritative.
- **FR-015**: Net expected value MUST account for the user's side, quantity, quoted economics, modeled
  expected payoff, and applicable fees without implying an executable or guaranteed return.
- **FR-016**: Every displayed input and result MUST be classified as observed, model-estimated,
  simulated, user-provided, adjusted, or unavailable, as applicable.
- **FR-017**: Every analysis MUST identify its observation time, data source, model/configuration
  version, and whether any fallback was used.
- **FR-018**: The product MUST provide a deterministic demo scenario that completes the entire
  waterfall without live services and produces repeatable results.
- **FR-019**: When live data is unavailable or incomplete, the product MUST offer the deterministic
  scenario rather than silently substituting simulated values into a live analysis.
- **FR-020**: Unsupported combo structures MUST return a clear explanation of the limitation and MUST
  NOT return a fabricated fair value.
- **FR-021**: Historical validation MUST fit each evaluated estimate using only observations available
  before that estimate's evaluation time.
- **FR-022**: Historical validation MUST report the fitting window, evaluation window, sample size,
  selected error measures, and material data limitations.
- **FR-023**: Historical validation and current estimates MUST state that model output and past
  performance do not guarantee future accuracy or trading profit.
- **FR-024**: Repeating an analysis with identical inputs and the same model/configuration version MUST
  produce identical values, rounding, classifications, and disclosures.
- **FR-025**: The product MUST remain analytics-only and MUST NOT place, route, or represent completion
  of a real-money trade.

### Key Entities *(include if feature involves data)*

- **Contract Leg**: One component of a combo, including its underlying outcome, direction, threshold
  or event condition, settlement rule, payoff contribution, probability, timing, and provenance.
- **Combo Definition**: The ordered set of two to four legs and the rules that determine the combo's
  payoff across possible joint outcomes.
- **RFQ Quote**: The quoted economics presented to the user, including intended side, price or amount,
  quantity, observation time, and source.
- **Market Input Set**: The probability and historical observations used for an analysis, with source,
  timestamps, freshness, and observed/estimated/simulated classifications.
- **Correlation Estimate**: The dependence information for the relevant underlying outcomes, including
  historical window, sample size, transformations, limitations, and disclosed adjustments.
- **Fee Assessment**: The applicable fee result and the verified rule or explicit assumption behind
  it, including status, effective time, quantity, and quote inputs.
- **Waterfall Result**: The staged independence, correlation, quote, and fee values; final net expected
  value; units; rounding; provenance; model version; and disclosures.
- **Validation Summary**: Time-ordered historical evaluation metadata and error measures, including
  sample sufficiency and limitations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time user can complete the canonical combo analysis and identify all four
  waterfall stages in under 60 seconds without developer assistance.
- **SC-002**: At least 95% of valid demo analyses present a complete result within 3 seconds under
  single-presenter hackathon conditions.
- **SC-003**: Across 10 consecutive runs, the canonical deterministic scenario produces identical
  displayed values, classifications, disclosures, and rounding 100% of the time.
- **SC-004**: In acceptance testing, 100% of displayed values identify whether they are observed,
  estimated, simulated, user-provided, adjusted, or unavailable.
- **SC-005**: In acceptance testing, 100% of unsupported or incomplete combos are blocked with a
  specific limitation or corrective message and no fabricated fair value.
- **SC-006**: Four out of five representative test users can correctly explain the difference between
  the quote, model estimate, fee amount, and net expected value after one unaided walkthrough.
- **SC-007**: A loss of live-data access does not prevent completion of the canonical deterministic
  demonstration, and the fallback is visibly identified within 5 seconds.
- **SC-008**: An audit of every historical-validation fixture confirms that 100% of evaluated
  predictions use only information available before their evaluation time.
- **SC-009**: Acceptance review finds zero instances where an estimate is described as objectively
  correct, a quote difference is described as guaranteed profit, or an unverified fee is presented
  as authoritative.

## Assumptions

- The hackathon release serves a single anonymous user at a time and does not require accounts,
  permissions, saved portfolios, or multi-user collaboration.
- The primary user is a retail trader or hackathon judge who understands basic event-contract terms
  but may not understand copulas or dependence modeling.
- The demo scope supports combos with two to four legs. Additional leg counts are deferred until the
  model and experience are validated.
- A documented subset of settlement and payoff structures will be supported. Unsupported structures
  are identified explicitly rather than approximated silently.
- Quote and fee economics use the units and currency applicable to the selected Kalshi market, with
  all units shown to the user.
- Public live market data is best-effort and may be delayed, incomplete, or unavailable.
- The canonical deterministic fixture contains no user, account, credential, or non-public market
  information and is safe to commit to the public repository.
- Historical validation is an explanatory credibility feature, not a claim of profitability or a
  substitute for independent trading judgment.
- No real-money trade execution, account connection, custody, personalized advice, or production
  compliance workflow is part of this feature.
