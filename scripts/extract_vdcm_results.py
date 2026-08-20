#!/usr/bin/env python3
"""
Extract VDCM developmental simulation results for cross-study rank-reversal analysis.
Source: immutable VDCM developmental results
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

# Source paths
VDCM_BASE = Path(__file__).parent.parent.parent / "applied-ai-research-lab" / "storypoints-age-of-ai"
VDCM_RESULTS = VDCM_BASE / "papers" / "thinkai-2026" / "results" / "developmental_simulation_v2"

def extract_vdcm_data():
    """Extract VDCM comparator performance across scenarios."""
    
    summary_file = VDCM_RESULTS / "scenario_summary.csv"
    brier_file = VDCM_RESULTS / "scenario_model_brier.csv"
    
    # Count scenario wins per model
    scenario_wins = defaultdict(int)
    brier_scores = defaultdict(list)
    
    # Read scenario summary
    with open(summary_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            winner = row['descriptive_lowest_brier_model']
            scenario_wins[winner] += 1
    
    # Read brier scores
    with open(brier_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row['model']
            brier = float(row['brier_score'])
            brier_scores[model].append(brier)
    
    # Aggregate results
    results = []
    all_models = set(scenario_wins.keys()) | set(brier_scores.keys())
    
    for model_id in all_models:
        wins = scenario_wins.get(model_id, 0)
        scores = brier_scores.get(model_id, [])
        mean_brier = sum(scores) / len(scores) if scores else 0.0
        
        # Simple criteria: scenario wins and brier score quality
        criteria_passed = 0
        failed_criteria = []
        
        if wins >= 2:
            criteria_passed += 1
        else:
            failed_criteria.append("scenario_wins")
        
        if mean_brier < 0.20:
            criteria_passed += 1
        else:
            failed_criteria.append("brier_threshold")
        
        results.append({
            "study": "VDCM",
            "method_id": model_id,
            "single_metric_value": 1.0 - mean_brier,  # Higher is better
            "single_metric_name": "inverse_mean_brier",
            "mean_brier_score": mean_brier,
            "scenario_wins": wins,
            "total_scenarios": 11,
            "criteria_passed": criteria_passed,
            "criteria_total": 2,
            "failed_criteria": failed_criteria,
            "gate_decision": "DEVELOPMENTAL"
        })
    
    return results

def main():
    """Main extraction routine."""
    print("Extracting VDCM results...")
    
    try:
        results = extract_vdcm_data()
        
        # Save extracted data
        output_file = Path(__file__).parent.parent / "studies" / "cross-study" / "data" / "vdcm_extracted.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Extracted {len(results)} VDCM comparator results")
        print(f"Saved to: {output_file}")
        print("NOTE: Placeholder data - needs actual VDCM result files")
        
    except Exception as e:
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
