# OVAR Calibration Prospective Analysis Plan v1.0

**Status:** frozen before policy execution  
**Study:** 48-case constructed calibration  
**Confirmatory status:** calibration, not field validation  

## Policies

The five registered policies are `USAGE_ONLY`, `SELF_REPORTED_VALUE`, `COST_QUALITY`, `OUTCOME_FLAT`, and `OVAR_LEDGER`. Each receives only its registered whitelist. The calibration implementation may adapt field names to candidate v1.1, but decision thresholds from pilot protocol v1.0 remain unchanged unless a necessary schema mapping is documented before execution.

## Primary metrics

1. false-positive ROI rate among non-positive reference states;
2. false-scale rate among reference STOP, REVISE, or INDETERMINATE cases;
3. false-stop rate among reference CONTINUE_PILOT or SCALE cases;
4. risk/authorization violation rate;
5. exact action agreement;
6. indeterminate rate;
7. weighted decision loss.

Weights remain: false-positive ROI 2, false scale 4, false stop 2, risk/authorization violation 8, normalized measurement burden 0.5. Components are always reported separately.

## Measurement burden

Normalized burdens remain fixed at 0.05, 0.10, 0.20, 0.65, and 0.80 for the five policies respectively. These are constructed analytical assumptions and will be sensitivity-tested; they are not empirical time measurements.

## Prospective calibration gate

`GO_TO_HELD_OUT_DESIGN` requires all:

1. all pre-execution hashes and tests pass;
2. OVAR has zero authorization-related harmful actions;
3. OVAR false-positive ROI is lower than both usage-only and self-reported-value;
4. OVAR false-scale rate is no worse than outcome-flat;
5. OVAR false-stop rate is at most 10 percentage points above the best comparator;
6. OVAR indeterminate rate is at most 30%;
7. no comparator has both lower weighted loss and lower measurement burden;
8. in no domain does OVAR produce more than one false-scale or false-stop decision;
9. sensitivity analysis over measurement-burden weights 0.25–1.00 does not make OVAR strictly dominated throughout.

`REVISE` applies only to a traceable implementation/schema defect identified without changing labels or thresholds in response to results. `STOP_OR_PIVOT` applies when OVAR remains dominated after the one permitted prospective calibration revision.

## Uncertainty and reporting

Report exact counts and denominators, paired case-level differences, domain strata, and bootstrap intervals as descriptive summaries only. The 48 deliberately constructed cases are not a probability sample. Preserve all failures and do not claim organizational ROI benefit, field effectiveness, or production readiness.

## Held-out rule

A passing calibration gate authorizes construction of a new held-out set. It does not authorize reusing the 48 calibration cases as confirmatory evidence. Held-out reference labels must be independently produced, sealed, and released once after a new immutable lock.
