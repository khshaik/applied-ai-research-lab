#!/usr/bin/env python3
"""
Extract OVAR v1.0 calibration results for cross-study rank-reversal analysis.
Source: immutable OVAR v1.0 calibration results
"""

import json
from pathlib import Path

# Source paths
OVAR_BASE = Path(__file__).parent.parent.parent / "applied-ai-research-lab" / "value-aware-enterprise-ai-tokenomics"
OVAR_RESULTS = OVAR_BASE / "research" / "studies" / "ovar" / "calibration" / "results" / "calibration_v1.0"

def extract_ovar_data():
    """Extract OVAR v1.0 policy decisions and gate results."""
    
    gate_file = OVAR_RESULTS / "calibration_gate.json"
    decisions_file = OVAR_RESULTS / "policy_decisions.json"
    
    results = []
    
    # Load gate decision
    with open(gate_file) as f:
        gate_data = json.load(f)
    
    # Extract per-policy metrics from policy_summaries
    for policy_data in gate_data.get("policy_summaries", []):
        
        policy_id = policy_data.get("policy", "UNKNOWN")
        rates = policy_data.get("rates", {})
        
        # Extract metrics
        false_roi_rate = rates.get("false_positive_roi", 0)
        false_scale_rate = rates.get("false_scale", 0)
        false_stop_rate = rates.get("false_stop", 0)
        auth_violations = rates.get("authorization_violation", 0)
        indeterminate_rate = rates.get("indeterminate", 0)
        
        # Count criteria passed
        criteria_passed = 0
        failed_criteria = []
        
        criteria_checks = [
            ("false_roi", false_roi_rate < 0.3),
            ("false_scale", false_scale_rate <= 0.15),
            ("false_stop", false_stop_rate <= 0.25),
            ("authorization", auth_violations == 0),
            ("indeterminate", indeterminate_rate <= 0.30)
        ]
        
        for criterion, passed in criteria_checks:
            if passed:
                criteria_passed += 1
            else:
                failed_criteria.append(criterion)
        
        results.append({
            "study": "OVAR",
            "method_id": policy_id,
            "single_metric_value": 1.0 - false_roi_rate,  # ROI reduction
            "single_metric_name": "roi_reduction_rate",
            "false_scale_rate": false_scale_rate,
            "false_stop_rate": false_stop_rate,
            "authorization_violations": auth_violations,
            "indeterminate_rate": indeterminate_rate,
            "criteria_passed": criteria_passed,
            "criteria_total": 9,
            "failed_criteria": failed_criteria,
            "gate_decision": policy_data.get("gate_decision", "UNKNOWN")
        })
    
    return results

def main():
    """Main extraction routine."""
    print("Extracting OVAR v1.0 results...")
    
    try:
        results = extract_ovar_data()
        
        # Save extracted data
        output_file = Path(__file__).parent.parent / "studies" / "cross-study" / "data" / "ovar_extracted.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Extracted {len(results)} OVAR policy results")
        print(f"Saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: Source file not found - {e}")
        print("Verify OVAR results location")
    except Exception as e:
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
