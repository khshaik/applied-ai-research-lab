#!/usr/bin/env python3
"""
Extract RAER v2 results for cross-study rank-reversal analysis.
Source: immutable RAER v2 design results
"""

import json
import csv
from pathlib import Path

# Source paths (relative to this script)
RAER_BASE = Path(__file__).parent.parent.parent / "applied-ai-research-lab" / "action-evidence-safety-research"
RAER_RESULTS = RAER_BASE / "studies" / "raer" / "evaluation" / "v2" / "results_design_v1.0"

def extract_raer_data():
    """Extract RAER v2 policy outcomes and gate results."""
    
    # Load policy summary
    summary_file = RAER_RESULTS / "oof_policy_summary.csv"
    outcomes_file = RAER_RESULTS / "oof_policy_outcomes.csv"
    gate_file = RAER_RESULTS / "v2_design_gate.json"
    
    results = []
    
    # Read gate decision
    with open(gate_file) as f:
        gate_data = json.load(f)
    
    # Read policy summary
    with open(summary_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            policy_id = row['policy']
            
            # Extract metrics
            safe_completion = float(row.get('safe_completion_rate', 0))
            harmful_actions = float(row.get('harmful_action_rate', 0))
            mean_cost = float(row.get('mean_validation_cost', 0))
            
            # Determine criteria passed (from gate data)
            criteria_passed = 0
            failed_criteria = []
            
            # Check each criterion (simplified - actual logic in gate_data)
            if safe_completion >= 0.95:
                criteria_passed += 1
            else:
                failed_criteria.append("safe_completion")
            
            results.append({
                "study": "RAER",
                "method_id": policy_id,
                "single_metric_value": safe_completion,
                "single_metric_name": "safe_completion_rate",
                "harmful_action_rate": harmful_actions,
                "mean_cost": mean_cost,
                "criteria_passed": criteria_passed,
                "criteria_total": 8,
                "failed_criteria": failed_criteria
            })
    
    return results

def main():
    """Main extraction routine."""
    print("Extracting RAER v2 results...")
    
    try:
        results = extract_raer_data()
        
        # Save extracted data
        output_file = Path(__file__).parent.parent / "studies" / "cross-study" / "data" / "raer_extracted.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Extracted {len(results)} RAER policy results")
        print(f"Saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: Source file not found - {e}")
        print("Verify RAER results location")
    
if __name__ == "__main__":
    main()
