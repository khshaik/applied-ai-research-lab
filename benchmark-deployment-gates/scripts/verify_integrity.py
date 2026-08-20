#!/usr/bin/env python3
"""
Verify data integrity and analysis completeness.
"""

import json
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "studies" / "cross-study" / "data"
RESULTS_DIR = PROJECT_ROOT / "studies" / "cross-study" / "results"

def compute_file_hash(file_path):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def verify_data_extraction():
    """Verify all extraction outputs exist."""
    print("Verifying data extraction...")
    
    required_files = [
        DATA_DIR / "raer_extracted.json",
        DATA_DIR / "ovar_extracted.json",
        DATA_DIR / "vdcm_extracted.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✓ {file_path.name}")
        else:
            print(f"  ✗ {file_path.name} - MISSING")
            all_exist = False
    
    return all_exist

def verify_analysis_results():
    """Verify analysis outputs exist."""
    print("\nVerifying analysis results...")
    
    required_files = [
        RESULTS_DIR / "rank_reversal_analysis.json",
        RESULTS_DIR / "threshold_sensitivity.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✓ {file_path.name}")
            
            # Verify JSON is valid
            try:
                with open(file_path) as f:
                    json.load(f)
                print(f"    → Valid JSON")
            except json.JSONDecodeError as e:
                print(f"    → Invalid JSON: {e}")
                all_exist = False
        else:
            print(f"  ✗ {file_path.name} - MISSING")
            all_exist = False
    
    return all_exist

def verify_hypothesis_outcomes():
    """Verify hypothesis test outcomes."""
    print("\nVerifying hypothesis outcomes...")
    
    results_file = RESULTS_DIR / "rank_reversal_analysis.json"
    sensitivity_file = RESULTS_DIR / "threshold_sensitivity.json"
    
    if not results_file.exists() or not sensitivity_file.exists():
        print("  ✗ Required result files missing")
        return False
    
    with open(results_file) as f:
        rank_results = json.load(f)
    
    with open(sensitivity_file) as f:
        sensitivity_results = json.load(f)
    
    # Check H1
    h1_result = rank_results["summary"]["hypothesis_h1_result"]
    h1_rate = rank_results["summary"]["overall_reversal_rate"]
    print(f"  H1 (Rank Reversals ≥20%): {h1_result} ({h1_rate:.1%})")
    
    # Check H3
    h3_result = sensitivity_results["summary"]["hypothesis_h3_result"]
    h3_rate = sensitivity_results["summary"]["overall_instability_rate"]
    print(f"  H3 (Instability ≥15%): {h3_result} ({h3_rate:.1%})")
    
    return True

def main():
    """Main verification routine."""
    print("="*60)
    print("BENCHMARK DEPLOYMENT GATES - INTEGRITY VERIFICATION")
    print("="*60)
    
    checks = [
        verify_data_extraction(),
        verify_analysis_results(),
        verify_hypothesis_outcomes()
    ]
    
    print("\n" + "="*60)
    if all(checks):
        print("✓ ALL CHECKS PASSED")
    else:
        print("✗ SOME CHECKS FAILED")
    print("="*60)

if __name__ == "__main__":
    main()
