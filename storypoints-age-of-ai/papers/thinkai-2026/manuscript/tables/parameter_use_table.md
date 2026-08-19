# Table — Developmental simulation parameter provenance

**Source registry:** `simulation/configs/parameter_registry.json`  
**Source SHA-256:**
`5d43a55fc92ec43c3e2e028b8d2caa05a25907d6c4a4daea56f3cdf0f6635e16`

| Input family | Executable path | Provenance/use class | Permitted interpretation | Prohibited interpretation |
|---|---|---|---|---|
| Planning horizon | `time_model.*` | Class I illustrative calibration | Finite-horizon mechanism fixture | Observed sprint or organizational duration |
| Role capacity | `role_pools.*.*` | Class I illustrative calibration | Hypothetical constrained-role capacity | Actual staffing, productivity, or human attention |
| Portfolio arrivals | `arrival_models.*.parameters.*` | Class I illustrative calibration | Fixed synthetic load scenarios | Empirical work-arrival distribution |
| Role-stage demand | `demand_models.*.base_distribution.*` | Class I illustrative calibration | Fixed/triangular service-demand mechanisms | Measured human touch time or elapsed pull-request duration |
| Calendars and blackouts | `capacity_calendars.*.*` | Class I illustrative calibration | Explicit availability/pause mechanics | Observed team calendars or utilization |
| Rework routing | `rework_models.*.*` | Class I illustrative calibration | Bounded rework-loop behavior | Empirical rework probability or gate benefit |
| World truth parameters | `data_generating_worlds.*.truth_parameters.*` | Class I; literature supplies directional mechanisms only | Heterogeneous mechanism and stress worlds | Universal AI speedup, review amplification, or gate-failure multiplier |
| Work-item/PDD fields | `work_item_templates.*.*` | Class I illustrative comparator input | Structural task profiles and equal-information comparator fixtures | Validated cognitive load, content-valid RSDRI score, or organization-calibrated estimate |
| Evaluation rules | `evaluation_rules.*` | Prespecified design control; not empirical calibration | Transparent synthetic decision convention | Empirical materiality, cost, or deployment threshold |

## Summary

All active calibration and comparator inputs remain Class I. Literature records
support the existence and direction of selected mechanisms but do not supply a
compatible numerical transformation for role-stage service time, capacity,
arrivals, gate outcomes, or rework. The simulation may therefore demonstrate
conditional model behavior only. The preregistered evaluation rules are design
choices, not observed parameters.

