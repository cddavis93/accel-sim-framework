#!/usr/bin/env python3
"""
Analyze existing simulation results to show current L1 cache bypassing data.

This script analyzes the existing simulation output files to demonstrate
what the current L1 cache bypassing implementation looks like.
"""

import os
import re
import json
from pathlib import Path

def analyze_existing_simulation():
    """Analyze the existing simulation results."""
    print("🔍 Analyzing Existing Simulation Results")
    print("=" * 50)
    
    # Path to existing simulation output
    output_file = "sim_run_12.8/vectoradd/NO_ARGS/A100/vectoradd-NO_ARGS.accelsim-commit-39eb185_modified_0.0_25-07-18-17-53-02gpgpu-sim_git-commit-3364474_modified_0.0.o15"
    
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return
    
    print(f"📄 Analyzing: {output_file}")
    
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Extract configuration
    config_match = re.search(r'-gpgpu_gmem_skip_L1D\s+(\d+)', content)
    if config_match:
        skip_l1d = int(config_match.group(1))
        print(f"\n📋 Configuration:")
        print(f"  -gpgpu_gmem_skip_L1D: {skip_l1d}")
        print(f"  L1 Cache: {'BYPASSED' if skip_l1d == 1 else 'ENABLED'}")
    
    # Extract L1 cache statistics
    print(f"\n📊 L1 Cache Statistics:")
    l1_stats = {}
    
    l1_patterns = {
        'Global Read Hits': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT\]\s*=\s*(\d+)',
        'Global Read Misses': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[MISS\]\s*=\s*(\d+)',
        'Global Read Total': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)',
        'Global Write Hits': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[HIT\]\s*=\s*(\d+)',
        'Global Write Misses': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[MISS\]\s*=\s*(\d+)',
        'Global Write Total': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[TOTAL_ACCESS\]\s*=\s*(\d+)'
    }
    
    for label, pattern in l1_patterns.items():
        match = re.search(pattern, content)
        if match:
            value = int(match.group(1))
            l1_stats[label] = value
            print(f"  {label}: {value}")
        else:
            l1_stats[label] = 0
            print(f"  {label}: 0")
    
    # Calculate hit rates
    if l1_stats['Global Read Total'] > 0:
        read_hit_rate = (l1_stats['Global Read Hits'] / l1_stats['Global Read Total']) * 100
        print(f"  Global Read Hit Rate: {read_hit_rate:.2f}%")
    
    if l1_stats['Global Write Total'] > 0:
        write_hit_rate = (l1_stats['Global Write Hits'] / l1_stats['Global Write Total']) * 100
        print(f"  Global Write Hit Rate: {write_hit_rate:.2f}%")
    
    # Extract L2 cache statistics
    print(f"\n📊 L2 Cache Statistics:")
    l2_stats = {}
    
    l2_patterns = {
        'Total Accesses': r'L2_total_cache_accesses\s*=\s*(\d+)',
        'Total Misses': r'L2_total_cache_misses\s*=\s*(\d+)',
        'Miss Rate': r'L2_total_cache_miss_rate\s*=\s*([\d.]+)',
        'Global Read Hits': r'L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT\]\s*=\s*(\d+)',
        'Global Read Misses': r'L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[MISS\]\s*=\s*(\d+)',
        'Global Write Hits': r'L2_cache_stats_breakdown\[GLOBAL_ACC_W\]\[HIT\]\s*=\s*(\d+)',
        'Global Write Misses': r'L2_cache_stats_breakdown\[GLOBAL_ACC_W\]\[MISS\]\s*=\s*(\d+)'
    }
    
    for label, pattern in l2_patterns.items():
        match = re.search(pattern, content)
        if match:
            if label == 'Miss Rate':
                value = float(match.group(1))
            else:
                value = int(match.group(1))
            l2_stats[label] = value
            print(f"  {label}: {value}")
        else:
            l2_stats[label] = 0
            print(f"  {label}: 0")
    
    # Calculate L2 hit rate
    if l2_stats['Total Accesses'] > 0:
        l2_hit_rate = ((l2_stats['Total Accesses'] - l2_stats['Total Misses']) / l2_stats['Total Accesses']) * 100
        print(f"  L2 Hit Rate: {l2_hit_rate:.2f}%")
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"  L1 Total Accesses: {l1_stats['Global Read Total'] + l1_stats['Global Write Total']}")
    print(f"  L2 Total Accesses: {l2_stats['Total Accesses']}")
    print(f"  L2 Miss Rate: {l2_stats['Miss Rate']:.2f}%")
    
    # Save results
    results = {
        'config': {'skip_l1d': skip_l1d},
        'l1_cache': l1_stats,
        'l2_cache': l2_stats
    }
    
    with open('existing_simulation_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed analysis saved to: existing_simulation_analysis.json")
    
    return results

def show_configuration_comparison():
    """Show the configuration differences between L1 enabled and bypassed."""
    print(f"\n🔧 Configuration Comparison:")
    print("=" * 50)
    
    config_files = [
        ("L1 Enabled", "sim_run_12.8/vectoradd/NO_ARGS/A100/gpgpusim.config"),
        ("L1 Bypassed", "sim_run_12.8/vectoradd/NO_ARGS/A100/gpgpusim_l1bypass.config")
    ]
    
    for name, config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
            
            skip_match = re.search(r'-gpgpu_gmem_skip_L1D\s+(\d+)', content)
            if skip_match:
                skip_value = int(skip_match.group(1))
                print(f"  {name}: -gpgpu_gmem_skip_L1D {skip_value}")
            else:
                print(f"  {name}: -gpgpu_gmem_skip_L1D not found")
        else:
            print(f"  {name}: Config file not found")

def main():
    """Main function to analyze existing results."""
    print("🚀 L1 Cache Bypassing Analysis")
    print("=" * 50)
    
    # Analyze existing simulation results
    results = analyze_existing_simulation()
    
    # Show configuration comparison
    show_configuration_comparison()
    
    print(f"\n✅ Analysis complete!")
    print(f"💡 To run actual simulations, use: python run_l1_bypass_test.py")

if __name__ == "__main__":
    main() 