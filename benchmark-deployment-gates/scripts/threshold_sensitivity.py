#!/usr/bin/env python3
"""
Threshold sensitivity analysis for deployment gate decisions.
Tests decision stability under threshold perturbations.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "studies" / "cross-study" / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "studies" / "cross-study" / "results"

def apply_threshold(value, threshold):
    """Apply threshold decision rule."""
    return "PASS" if value >= threshold else "FAIL"

def sensitivity_analysis(study_data, perturbations=[-0.20, -0.10, 0.0, 0.10, 0.20]):
    """Analyze decision stability under threshold perturbations."""
    
    results = []
    
    for method in study_data:
        base_value = method['single_metric_value']
        base_threshold = 0.5  # Default threshold
        
        decisions = {}
        for perturbation in perturbations:
            perturbed_threshold = base_threshold * (1 + perturbation)
            decisions[f"{perturbation:+.0%}"] = apply_threshold(base_value, perturbed_threshold)
        
        # Check for decision changes
        unique_decisions = set(decisions.values())
        is_unstable = len(unique_decisions) > 1
        
        results.append({
            "method_id": method['method_id'],
            "base_value": base_value,
            "decisions": decisions,
            "is_unstable": is_unstable,
            "decision_changes": len(unique_decisions) - 1
        })
    
    return results

def main():
    """Main sensitivity analysis routine."""
    print("Running threshold sensitivity analysis...")
    
    # Load data
    all_data = {}
    for study in ["raer", "ovar", "vdcm"]:
        file_path = DATA_DIR / f"{study}_extracted.json"
        if file_path.exists():
            with open(file_path) as f:
                all_data[study] = json.load(f)
    
    # Analysis results
    results = {
        "sensitivity_by_study": {},
        "summary": {}
    }
    
    total_unstable = 0
    total_cases = 0
    
    # Analyze each study
    for study_name, study_data in all_data.items():
        if not study_data:
            continue
        
        print(f"\nAnalyzing {study_name.upper()}...")
        
        sensitivity = sensitivity_analysis(study_data)
        unstable_count = sum(1 for s in sensitivity if s['is_unstable'])
        
        results["sensitivity_by_study"][study_name] = {
            "sensitivity_results": sensitivity,
            "unstable_count": unstable_count,
            "total_cases": len(study_data),
            "instability_rate": unstable_count / len(study_data) if study_data else 0
        }
        
        total_unstable += unstable_count
        total_cases += len(study_data)
        
        print(f"  Unstable cases: {unstable_count}/{len(study_data)} ({unstable_count/len(study_data)*100:.1f}%)")
    
    # Overall summary
    results["summary"] = {
        "total_unstable": total_unstable,
        "total_cases": total_cases,
        "overall_instability_rate": total_unstable / total_cases if total_cases > 0 else 0,
        "hypothesis_h3_threshold": 0.15,
        "hypothesis_h3_result": "PASS" if (total_unstable / total_cases) >= 0.15 else "FAIL"
    }
    
    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "threshold_sensitivity.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Overall Instability Rate: {results['summary']['overall_instability_rate']:.1%}")
    print(f"H3 Threshold: {results['summary']['hypothesis_h3_threshold']:.1%}")
    print(f"H3 Result: {results['summary']['hypothesis_h3_result']}")
    print(f"{'='*60}")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
