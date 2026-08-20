#!/usr/bin/env python3
"""
Generate visualizations for rank reversal and threshold sensitivity analysis.
"""

import json
from pathlib import Path
import sys

# Check for matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

RESULTS_DIR = Path(__file__).parent.parent / "studies" / "cross-study" / "results"
FIGURES_DIR = Path(__file__).parent.parent / "papers" / "thinkai-2026" / "figures"

def generate_rank_reversal_heatmap():
    """Generate heatmap showing rank reversals across studies."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("Skipping heatmap generation - matplotlib not available")
        return
    
    # Load results
    results_file = RESULTS_DIR / "rank_reversal_analysis.json"
    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        return
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    studies = list(results["rank_reversals"].keys())
    reversal_rates = [results["rank_reversals"][s]["reversal_rate"] for s in studies]
    
    # Bar plot
    bars = ax.bar(studies, reversal_rates, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax.axhline(y=0.20, color='r', linestyle='--', label='H1 Threshold (20%)')
    
    ax.set_ylabel('Rank Reversal Rate')
    ax.set_title('Rank Reversals: Single-Metric vs. Multi-Criteria Evaluation')
    ax.set_ylim(0, 1.0)
    ax.legend()
    
    # Save
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_file = FIGURES_DIR / "rank_reversal_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def generate_criteria_failure_chart():
    """Generate chart showing multi-criteria failure patterns."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("Skipping failure chart - matplotlib not available")
        return
    
    # Load results
    results_file = RESULTS_DIR / "rank_reversal_analysis.json"
    if not results_file.exists():
        return
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    studies = list(results["multi_criteria_failures"].keys())
    failure_counts = [results["multi_criteria_failures"][s]["failure_count"] for s in studies]
    
    # Bar plot
    bars = ax.bar(studies, failure_counts, color=['#2E86AB', '#A23B72', '#F18F01'])
    
    ax.set_ylabel('Methods with ≥2 Criteria Failures')
    ax.set_title('Methods Passing Single Metric but Failing Multiple Deployment Criteria')
    ax.legend()
    
    # Save
    output_file = FIGURES_DIR / "criteria_failure_patterns.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def generate_threshold_sensitivity_chart():
    """Generate threshold sensitivity visualization."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("Skipping sensitivity chart - matplotlib not available")
        return
    
    # Load results
    results_file = RESULTS_DIR / "threshold_sensitivity.json"
    if not results_file.exists():
        return
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    studies = list(results["sensitivity_by_study"].keys())
    instability_rates = [results["sensitivity_by_study"][s]["instability_rate"] for s in studies]
    
    # Bar plot
    bars = ax.bar(studies, instability_rates, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax.axhline(y=0.15, color='r', linestyle='--', label='H3 Threshold (15%)')
    
    ax.set_ylabel('Decision Instability Rate')
    ax.set_title('Decision Stability Under ±10% Threshold Perturbation')
    ax.set_ylim(0, 1.0)
    ax.legend()
    
    # Save
    output_file = FIGURES_DIR / "threshold_sensitivity.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def main():
    """Generate all visualizations."""
    print("Generating visualizations...")
    
    if not MATPLOTLIB_AVAILABLE:
        print("\nTo generate figures, install matplotlib:")
        print("  pip install matplotlib")
        return
    
    generate_rank_reversal_heatmap()
    generate_criteria_failure_chart()
    generate_threshold_sensitivity_chart()
    
    print("\nAll visualizations generated successfully!")

if __name__ == "__main__":
    main()
