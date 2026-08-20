#!/usr/bin/env python3
"""
Rank reversal analysis across RAER, OVAR, and VDCM studies.
Compares single-metric rankings with multi-criteria gate outcomes.
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "studies" / "cross-study" / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "studies" / "cross-study" / "results"

def load_extracted_data():
    """Load all extracted study results."""
    data = {}
    
    for study in ["raer", "ovar", "vdcm"]:
        file_path = DATA_DIR / f"{study}_extracted.json"
        if file_path.exists():
            with open(file_path) as f:
                data[study] = json.load(f)
        else:
            print(f"Warning: {file_path} not found")
            data[study] = []
    
    return data

def compute_ranks(methods, metric_key, ascending=True):
    """Compute ranks for methods based on a metric."""
    sorted_methods = sorted(methods, key=lambda x: x[metric_key], reverse=not ascending)
    ranks = {}
    for rank, method in enumerate(sorted_methods, 1):
        ranks[method['method_id']] = rank
    return ranks

def analyze_rank_reversals(study_data):
    """Analyze rank reversals for a single study."""
    
    # Single-metric ranks (lower is better for most metrics)
    single_ranks = compute_ranks(study_data, 'single_metric_value', ascending=False)
    
    # Multi-criteria ranks (more criteria passed = better)
    multi_ranks = compute_ranks(study_data, 'criteria_passed', ascending=False)
    
    reversals = []
    for method in study_data:
        method_id = method['method_id']
        single_rank = single_ranks[method_id]
        multi_rank = multi_ranks[method_id]
        reversal_magnitude = abs(single_rank - multi_rank)
        
        if reversal_magnitude >= 2:
            reversals.append({
                "method_id": method_id,
                "single_rank": single_rank,
                "multi_rank": multi_rank,
                "reversal_magnitude": reversal_magnitude,
                "single_metric_value": method['single_metric_value'],
                "criteria_passed": method['criteria_passed'],
                "criteria_total": method['criteria_total']
            })
    
    return reversals, single_ranks, multi_ranks

def analyze_multi_criteria_failures(study_data):
    """Find methods passing single metric but failing multiple criteria."""
    
    failures = []
    for method in study_data:
        criteria_failed = method['criteria_total'] - method['criteria_passed']
        
        # Check if passes single metric threshold but fails >=2 criteria
        if method['single_metric_value'] > 0.5 and criteria_failed >= 2:
            failures.append({
                "method_id": method['method_id'],
                "single_metric_value": method['single_metric_value'],
                "criteria_passed": method['criteria_passed'],
                "criteria_failed": criteria_failed,
                "failed_criteria": method.get('failed_criteria', [])
            })
    
    return failures

def main():
    """Main analysis routine."""
    print("Running rank reversal analysis...")
    
    # Load data
    all_data = load_extracted_data()
    
    # Analysis results
    results = {
        "rank_reversals": {},
        "multi_criteria_failures": {},
        "summary": {}
    }
    
    total_reversals = 0
    total_methods = 0
    
    # Analyze each study
    for study_name, study_data in all_data.items():
        if not study_data:
            continue
        
        print(f"\nAnalyzing {study_name.upper()}...")
        
        # Rank reversals
        reversals, single_ranks, multi_ranks = analyze_rank_reversals(study_data)
        results["rank_reversals"][study_name] = {
            "reversals": reversals,
            "reversal_count": len(reversals),
            "total_methods": len(study_data),
            "reversal_rate": len(reversals) / len(study_data) if study_data else 0
        }
        
        # Multi-criteria failures
        failures = analyze_multi_criteria_failures(study_data)
        results["multi_criteria_failures"][study_name] = {
            "failures": failures,
            "failure_count": len(failures)
        }
        
        total_reversals += len(reversals)
        total_methods += len(study_data)
        
        print(f"  Reversals: {len(reversals)}/{len(study_data)} ({len(reversals)/len(study_data)*100:.1f}%)")
        print(f"  Multi-criteria failures: {len(failures)}")
    
    # Overall summary
    results["summary"] = {
        "total_reversals": total_reversals,
        "total_methods": total_methods,
        "overall_reversal_rate": total_reversals / total_methods if total_methods > 0 else 0,
        "hypothesis_h1_threshold": 0.20,
        "hypothesis_h1_result": "PASS" if (total_reversals / total_methods) >= 0.20 else "FAIL"
    }
    
    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "rank_reversal_analysis.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Overall Reversal Rate: {results['summary']['overall_reversal_rate']:.1%}")
    print(f"H1 Threshold: {results['summary']['hypothesis_h1_threshold']:.1%}")
    print(f"H1 Result: {results['summary']['hypothesis_h1_result']}")
    print(f"{'='*60}")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
