import unittest

from simulation.comparators import ComparatorSuite
from simulation.evaluation import (
    adjudicate_proposed_model,
    bottleneck_accuracy,
    brier_score,
    evaluate_forecasts,
    paired_brier_contrast,
    quantile_absolute_error,
    relative_brier_skill,
)


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "story_points": 5,
            "story_point_budget": 8,
            "hie_context_load": 0.10,
            "hie_interaction_load": 0.20,
            "hie_oversight_load": 0.15,
            "role_demand": {"development": 4, "qa": 9},
            "role_capacity": {"development": 8, "qa": 10},
            "role_stage_demand": {
                "development": {"implementation": 4},
                "qa": {"verification": 9},
            },
            "role_stage_capacity": {
                "development": {"implementation": 8},
                "qa": {"verification": 10},
            },
            "readiness_probability": 0.85,
            "rework_probability": 0.10,
            "dependency_block_probability": 0.05,
            "true_completion_probability": 0.72,
            "true_role_load": {"development": 0.55, "qa": 0.95},
        }

    def test_all_five_comparators_return_probabilities(self):
        forecasts = ComparatorSuite().forecast(self.item)
        self.assertEqual(set(forecasts), set(ComparatorSuite.names))
        self.assertTrue(all(0 <= p <= 1 for p in forecasts.values()))

    def test_task_only_models_abstain_from_bottleneck(self):
        suite = ComparatorSuite()
        self.assertIsNone(suite.predicted_bottleneck(self.item, "story_points"))
        self.assertIsNone(suite.predicted_bottleneck(self.item, "hie_compatible"))
        self.assertEqual(suite.predicted_bottleneck(self.item, "proposed_model"), "qa")

    def test_oracle_requires_truth_field(self):
        item = dict(self.item)
        del item["true_completion_probability"]
        with self.assertRaises(ValueError):
            ComparatorSuite().forecast(item)

    def test_proposed_discriminates_dependency_readiness_and_rework(self):
        suite = ComparatorSuite()
        favorable = dict(self.item)
        favorable.update(readiness_probability=1.0, rework_probability=0.0,
                         dependency_block_probability=0.0)
        adverse = dict(favorable)
        adverse.update(readiness_probability=0.5, rework_probability=0.4,
                       dependency_block_probability=0.3)
        self.assertGreater(suite.proposed_model(favorable), suite.proposed_model(adverse))
        # Fair comparator boundary: the same added signals do not alter models
        # that are not allowed to consume them.
        self.assertEqual(suite.story_points(favorable), suite.story_points(adverse))
        self.assertEqual(suite.hie_compatible(favorable), suite.hie_compatible(adverse))
        self.assertEqual(suite.simple_role_load(favorable), suite.simple_role_load(adverse))

    def test_proposed_uses_role_stage_inputs_not_aggregate_shortcut(self):
        suite = ComparatorSuite()
        baseline = dict(self.item)
        changed = dict(baseline)
        changed["role_stage_demand"] = {
            "development": {"implementation": 7.6},
            "qa": {"verification": 9},
        }
        self.assertNotEqual(suite.proposed_model(baseline), suite.proposed_model(changed))
        self.assertEqual(suite.simple_role_load(baseline), suite.simple_role_load(changed))

    def test_non_oracle_forecasts_ignore_runtime_truth_fields(self):
        suite = ComparatorSuite()
        first = dict(self.item)
        second = dict(first)
        second.update(true_completion_probability=0.01,
                      true_role_load={"development": 99, "qa": 0.01})
        self.assertEqual(suite.forecast(first, include_oracle=False),
                         suite.forecast(second, include_oracle=False))


class EvaluationTests(unittest.TestCase):
    def test_brier_and_skill(self):
        self.assertAlmostEqual(brier_score([0.8, 0.2], [1, 0]), 0.04)
        self.assertAlmostEqual(relative_brier_skill(0.18, 0.20), 0.10)

    def test_evaluation_has_calibration_and_reference_skill(self):
        result = evaluate_forecasts(
            {"story_points": [0.7, 0.4, 0.8, 0.2], "proposed_model": [0.9, 0.1, 0.7, 0.2]},
            [1, 0, 1, 0],
            strongest_deployable="story_points",
            bins=2,
        )
        self.assertIn("calibration", result["proposed_model"])
        self.assertGreater(result["proposed_model"]["relative_brier_skill"], 0)

    def test_bottleneck_abstention_reported(self):
        result = bottleneck_accuracy(["qa", None, "security"], ["qa", "dev", "security"])
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["abstained_n"], 1)

    def test_secondary_quantile_error(self):
        self.assertAlmostEqual(quantile_absolute_error([1, 2, 3], [2, 3, 4], 0.5), 1.0)

    def test_paired_contrast_and_synthetic_adjudication(self):
        outcomes = [1, 0, 1, 0, 1, 0, 1, 0]
        candidate = [0.9, 0.1, 0.85, 0.15, 0.9, 0.1, 0.85, 0.15]
        reference = [0.65, 0.35, 0.6, 0.4, 0.65, 0.35, 0.6, 0.4]
        contrast = paired_brier_contrast(candidate, reference, outcomes)
        decision = adjudicate_proposed_model(
            contrast,
            [0.02, 0.03, 0.01, 0.04, 0.02],
            bottleneck_improvement=0.15,
        )
        self.assertGreater(contrast["ci95_lower"], 0)
        self.assertEqual(decision["synthetic_decision"], "retain_for_field_testing")


if __name__ == "__main__":
    unittest.main()
