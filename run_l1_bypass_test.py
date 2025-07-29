#!/usr/bin/env python3
"""
Comprehensive L1 Cache Bypassing Test Script for Accel-Sim Framework

This script actually runs the Accel-Sim simulator with different L1 cache bypassing
configurations and compares the results to verify that L1 bypassing works correctly.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path
import json

class L1BypassTester:
    def __init__(self):
        self.simulator_path = "gpu-simulator/bin/debug/accel-sim.out"
        self.config_dir = "sim_run_12.8/vectoradd/NO_ARGS/A100"
        self.traces_dir = f"{self.config_dir}/traces"
        self.results = {}
        
    def check_simulator_exists(self):
        """Check if the simulator binary exists."""
        if not os.path.exists(self.simulator_path):
            print(f"❌ Error: Simulator not found at {self.simulator_path}")
            return False
        print(f"✅ Found simulator at {self.simulator_path}")
        return True
    
    def run_simulation(self, config_name, config_file, output_file):
        """Run a simulation with the specified configuration."""
        print(f"\n🔄 Running simulation with {config_name}...")
        
        cmd = [
            f"./{self.simulator_path}",
            "-config", config_file,
            "-traces", self.traces_dir
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()
            
            # Save output to file
            with open(output_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n=== STDERR ===\n")
                    f.write(result.stderr)
            
            if result.returncode == 0:
                print(f"✅ Simulation completed successfully in {end_time - start_time:.2f}s")
                print(f"📄 Output saved to: {output_file}")
                return True
            else:
                print(f"❌ Simulation failed with return code {result.returncode}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Simulation timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False
    
    def extract_cache_statistics(self, output_file):
        """Extract cache statistics from simulation output."""
        print(f"📊 Extracting cache statistics from {output_file}")
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        stats = {
            'l1_cache': {},
            'l2_cache': {},
            'config': {}
        }
        
        # Extract L1 cache statistics
        l1_patterns = {
            'global_read_hit': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT\]\s*=\s*(\d+)',
            'global_read_miss': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[MISS\]\s*=\s*(\d+)',
            'global_read_total': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)',
            'global_write_hit': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[HIT\]\s*=\s*(\d+)',
            'global_write_miss': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[MISS\]\s*=\s*(\d+)',
            'global_write_total': r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_W\]\[TOTAL_ACCESS\]\s*=\s*(\d+)'
        }
        
        for key, pattern in l1_patterns.items():
            match = re.search(pattern, content)
            if match:
                stats['l1_cache'][key] = int(match.group(1))
            else:
                stats['l1_cache'][key] = 0
        
        # Extract L2 cache statistics
        l2_patterns = {
            'total_accesses': r'L2_total_cache_accesses\s*=\s*(\d+)',
            'total_misses': r'L2_total_cache_misses\s*=\s*(\d+)',
            'miss_rate': r'L2_total_cache_miss_rate\s*=\s*([\d.]+)',
            'global_read_hit': r'L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT\]\s*=\s*(\d+)',
            'global_read_miss': r'L2_cache_stats_breakdown\[GLOBAL_ACC_R\]\[MISS\]\s*=\s*(\d+)',
            'global_write_hit': r'L2_cache_stats_breakdown\[GLOBAL_ACC_W\]\[HIT\]\s*=\s*(\d+)',
            'global_write_miss': r'L2_cache_stats_breakdown\[GLOBAL_ACC_W\]\[MISS\]\s*=\s*(\d+)'
        }
        
        for key, pattern in l2_patterns.items():
            match = re.search(pattern, content)
            if match:
                if key == 'miss_rate':
                    stats['l2_cache'][key] = float(match.group(1))
                else:
                    stats['l2_cache'][key] = int(match.group(1))
            else:
                stats['l2_cache'][key] = 0
        
        # Extract configuration
        config_match = re.search(r'-gpgpu_gmem_skip_L1D\s+(\d+)', content)
        if config_match:
            stats['config']['skip_l1d'] = int(config_match.group(1))
        
        return stats
    
    def calculate_hit_rates(self, stats):
        """Calculate hit rates for L1 and L2 caches."""
        l1 = stats['l1_cache']
        l2 = stats['l2_cache']
        
        # L1 hit rates
        if l1['global_read_total'] > 0:
            l1['global_read_hit_rate'] = (l1['global_read_hit'] / l1['global_read_total']) * 100
        else:
            l1['global_read_hit_rate'] = 0
            
        if l1['global_write_total'] > 0:
            l1['global_write_hit_rate'] = (l1['global_write_hit'] / l1['global_write_total']) * 100
        else:
            l1['global_write_hit_rate'] = 0
        
        # L2 hit rates
        if l2['total_accesses'] > 0:
            l2['hit_rate'] = ((l2['total_accesses'] - l2['total_misses']) / l2['total_accesses']) * 100
        else:
            l2['hit_rate'] = 0
        
        return stats
    
    def print_comparison(self, l1_enabled_stats, l1_bypassed_stats):
        """Print a detailed comparison of the two configurations."""
        print("\n" + "="*80)
        print("L1 CACHE BYPASSING COMPARISON RESULTS")
        print("="*80)
        
        print(f"\n📋 Configuration:")
        print(f"  L1 Enabled:  -gpgpu_gmem_skip_L1D {l1_enabled_stats['config']['skip_l1d']}")
        print(f"  L1 Bypassed: -gpgpu_gmem_skip_L1D {l1_bypassed_stats['config']['skip_l1d']}")
        
        print(f"\n📊 L1 Cache Statistics:")
        print(f"{'Metric':<25} {'L1 Enabled':<15} {'L1 Bypassed':<15} {'Difference':<15}")
        print("-" * 70)
        
        l1_enabled = l1_enabled_stats['l1_cache']
        l1_bypassed = l1_bypassed_stats['l1_cache']
        
        metrics = [
            ('Global Read Hits', 'global_read_hit'),
            ('Global Read Misses', 'global_read_miss'),
            ('Global Read Total', 'global_read_total'),
            ('Global Read Hit Rate', 'global_read_hit_rate'),
            ('Global Write Hits', 'global_write_hit'),
            ('Global Write Misses', 'global_write_miss'),
            ('Global Write Total', 'global_write_total'),
            ('Global Write Hit Rate', 'global_write_hit_rate')
        ]
        
        for label, key in metrics:
            enabled_val = l1_enabled.get(key, 0)
            bypassed_val = l1_bypassed.get(key, 0)
            diff = bypassed_val - enabled_val
            
            if 'Rate' in label:
                print(f"{label:<25} {enabled_val:<15.2f} {bypassed_val:<15.2f} {diff:<+15.2f}")
            else:
                print(f"{label:<25} {enabled_val:<15} {bypassed_val:<15} {diff:<+15}")
        
        print(f"\n📊 L2 Cache Statistics:")
        print(f"{'Metric':<25} {'L1 Enabled':<15} {'L1 Bypassed':<15} {'Difference':<15}")
        print("-" * 70)
        
        l2_enabled = l1_enabled_stats['l2_cache']
        l2_bypassed = l1_bypassed_stats['l2_cache']
        
        l2_metrics = [
            ('Total Accesses', 'total_accesses'),
            ('Total Misses', 'total_misses'),
            ('Miss Rate', 'miss_rate'),
            ('Hit Rate', 'hit_rate')
        ]
        
        for label, key in l2_metrics:
            enabled_val = l2_enabled.get(key, 0)
            bypassed_val = l2_bypassed.get(key, 0)
            diff = bypassed_val - enabled_val
            
            if 'Rate' in label:
                print(f"{label:<25} {enabled_val:<15.2f} {bypassed_val:<15.2f} {diff:<+15.2f}")
            else:
                print(f"{label:<25} {enabled_val:<15} {bypassed_val:<15} {diff:<+15}")
    
    def verify_bypassing_works(self, l1_enabled_stats, l1_bypassed_stats):
        """Verify that L1 bypassing is working correctly."""
        print(f"\n🔍 VERIFICATION RESULTS:")
        
        l1_enabled = l1_enabled_stats['l1_cache']
        l1_bypassed = l1_bypassed_stats['l1_cache']
        
        # Check if L1 bypassing reduces L1 activity
        l1_enabled_total = l1_enabled['global_read_total'] + l1_enabled['global_write_total']
        l1_bypassed_total = l1_bypassed['global_read_total'] + l1_bypassed['global_write_total']
        
        print(f"  L1 Total Accesses (Enabled):  {l1_enabled_total}")
        print(f"  L1 Total Accesses (Bypassed): {l1_bypassed_total}")
        
        if l1_bypassed_total < l1_enabled_total:
            print(f"  ✅ L1 bypassing is working - reduced L1 accesses by {l1_enabled_total - l1_bypassed_total}")
        else:
            print(f"  ❌ L1 bypassing may not be working - L1 accesses not reduced")
        
        # Check if L2 activity increases when L1 is bypassed
        l2_enabled = l1_enabled_stats['l2_cache']
        l2_bypassed = l1_bypassed_stats['l2_cache']
        
        l2_enabled_total = l2_enabled['total_accesses']
        l2_bypassed_total = l2_bypassed['total_accesses']
        
        print(f"  L2 Total Accesses (L1 Enabled):  {l2_enabled_total}")
        print(f"  L2 Total Accesses (L1 Bypassed): {l2_bypassed_total}")
        
        if l2_bypassed_total > l2_enabled_total:
            print(f"  ✅ L1 bypassing is working - increased L2 accesses by {l2_bypassed_total - l2_enabled_total}")
        else:
            print(f"  ❌ L1 bypassing may not be working - L2 accesses not increased")
        
        # Overall verification
        if (l1_bypassed_total < l1_enabled_total and l2_bypassed_total > l2_enabled_total):
            print(f"\n🎉 VERIFICATION PASSED: L1 cache bypassing is working correctly!")
            return True
        else:
            print(f"\n❌ VERIFICATION FAILED: L1 cache bypassing may not be working correctly!")
            return False
    
    def run_comprehensive_test(self):
        """Run the comprehensive L1 bypassing test."""
        print("🚀 Starting Comprehensive L1 Cache Bypassing Test")
        print("=" * 60)
        
        # Check if simulator exists
        if not self.check_simulator_exists():
            return False
        
        # Define test configurations
        configs = [
            {
                'name': 'L1_Enabled',
                'config_file': f'{self.config_dir}/gpgpusim.config',
                'output_file': 'l1_enabled_simulation.out'
            },
            {
                'name': 'L1_Bypassed', 
                'config_file': f'{self.config_dir}/gpgpusim_l1bypass.config',
                'output_file': 'l1_bypassed_simulation.out'
            }
        ]
        
        # Run simulations
        for config in configs:
            success = self.run_simulation(
                config['name'],
                config['config_file'],
                config['output_file']
            )
            
            if not success:
                print(f"❌ Failed to run {config['name']} simulation")
                return False
            
            # Extract and analyze statistics
            stats = self.extract_cache_statistics(config['output_file'])
            stats = self.calculate_hit_rates(stats)
            self.results[config['name']] = stats
        
        # Compare results
        l1_enabled_stats = self.results['L1_Enabled']
        l1_bypassed_stats = self.results['L1_Bypassed']
        
        self.print_comparison(l1_enabled_stats, l1_bypassed_stats)
        
        # Verify bypassing works
        verification_passed = self.verify_bypassing_works(l1_enabled_stats, l1_bypassed_stats)
        
        # Save results to JSON
        with open('l1_bypass_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: l1_bypass_test_results.json")
        
        return verification_passed

def main():
    """Main function to run the L1 bypassing test."""
    tester = L1BypassTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n✅ L1 Cache Bypassing Test PASSED")
            sys.exit(0)
        else:
            print(f"\n❌ L1 Cache Bypassing Test FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 