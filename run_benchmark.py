import config
from main import run_simulation
import csv
import os
import shutil
import random
import numpy as np

def run_benchmark():
    strategies = ["HYBRID", "MOCS", "SPEA2"]
    FIXED_SEED = 100
    
    results_file = "benchmark_results.csv"
    
    # Reset File with Extended Header
    with open(results_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Scheduler', 'AverageLatency', 'TotalEnergy', 'TasksCompleted', 'DeadlineMissRate', 'Throughput', 'QTableSize', 'Epsilon'])

    print(f"--- 🏆 Starting Benchmark Comparison ---")
    config.TRAINING_MODE = False
    config.BENCHMARK_MODE = True
    
    # Use existing duration if set (e.g. from UI), otherwise default to 1000 for standalone runs
    if config.TASK_GENERATION_PERIOD == 100: # Default value in config.py
        config.TASK_GENERATION_PERIOD = 1000
        print(f"   [i] using default Benchmark Duration: {config.TASK_GENERATION_PERIOD}s")
    else:
        print(f"   [i] using Configured Duration: {config.TASK_GENERATION_PERIOD}s")

    # Detect Custom Configuration
    if config.FOG_NODES_CUSTOM_CONFIG:
        print(f"   [!] CUSTOM FOG CONFIG ACTIVE: {len(config.FOG_NODES_CUSTOM_CONFIG)} nodes defined.")
    if config.IOT_DEVICES_CUSTOM_CONFIG:
        print(f"   [!] CUSTOM IOT CONFIG ACTIVE: {len(config.IOT_DEVICES_CUSTOM_CONFIG)} devices defined.")
    
    for strategy in strategies:
        print(f"\n>>> Testing Strategy: {strategy}")
        
        # --- FAIRNESS ENFORCEMENT ---
        # Reset the seed so every scheduler faces the exact same 
        # 1. Fog Node Hardware Configuration
        # 2. Task Arrival Times and Properties
        random.seed(FIXED_SEED)
        np.random.seed(FIXED_SEED)
        
        config.SCHEDULER_TYPE = strategy
        
        # Run
        run_simulation(training_mode=False, benchmark_mode=True)
        
        # Preserve Task Data for detailed plotting
        if os.path.exists("task_data.csv"):
            new_name = f"task_data_{strategy}.csv"
            shutil.copy("task_data.csv", new_name)
            print(f"   [+] Saved detailed task data to {new_name}")

        # Preserve Fog Config for fairness verification
        if os.path.exists("fog_node_config.csv"):
            conf_name = f"fog_node_config_{strategy}.csv"
            shutil.copy("fog_node_config.csv", conf_name)
            print(f"   [+] Saved fog config to {conf_name}")
        
    print(f"\n--- Benchmark Complete. Results saved to {results_file} ---")

    # --- VERIFICATION STEP ---
    print("\n--- 🛡️ Verifying Fairness (Hardware Configuration Audit) ---")
    import pandas as pd
    
    configs = {}
    try:
        for strategy in strategies:
            filename = f"fog_node_config_{strategy}.csv"
            if os.path.exists(filename):
                configs[strategy] = pd.read_csv(filename)
            else:
                print(f"   [!] Missing config file for {strategy}")

        if len(configs) == len(strategies):
            base_strategy = strategies[0]
            base_config = configs[base_strategy]
            all_match = True
            
            for strategy in strategies[1:]:
                if not base_config.equals(configs[strategy]):
                    all_match = False
                    print(f"   [x] MISMATCH DETECTED: {base_strategy} vs {strategy}")
                    break
            
            if all_match:
                print("   ✅ SUCCESS: Fog Node Hardware was IDENTICAL for all runs.")
                print(f"      (Checked {len(base_config)} nodes across {len(strategies)} strategies)")
            else:
                print("   ❌ FAILURE: Hardware configurations differed between runs!")

            # --- TASK WORKLOAD VERIFICATION ---
            print("\n--- 🛡️ Verifying Fairness (Task Workload Audit) ---")
            task_files = {}
            for strategy in strategies:
                filename = f"task_data_{strategy}.csv"
                if os.path.exists(filename):
                    task_files[strategy] = pd.read_csv(filename)
                else:
                    print(f"   [!] Missing task data file for {strategy}")

            if len(task_files) == len(strategies):
                base_strategy = strategies[0]
                base_tasks = task_files[base_strategy]
                
                # Columns that define the workload (Input parameters)
                workload_cols = ['task_id', 'task_type', 'creation_time', 'task_cpu_required', 'task_data_size_mb', 'deadline']
                
                tasks_match = True
                for strategy in strategies[1:]:
                    compare_tasks = task_files[strategy]
                    # Compare only the workload columns
                    if not base_tasks[workload_cols].equals(compare_tasks[workload_cols]):
                        tasks_match = False
                        print(f"   [x] MISMATCH DETECTED: {base_strategy} vs {strategy}")
                        # Show first mismatch for debugging
                        diff = base_tasks[workload_cols].compare(compare_tasks[workload_cols])
                        print(diff.head())
                        break
                
                if tasks_match:
                    print("   ✅ SUCCESS: Task Workload was IDENTICAL for all runs.")
                    print(f"      (Checked {len(base_tasks)} tasks across {len(strategies)} strategies)")
                else:
                    print("   ❌ FAILURE: Task Workloads differed between runs!")

        else:
            print("   [!] Could not verify: Not all config files were generated.")
            
    except Exception as e:
        print(f"   [!] Verification failed with error: {e}")
    
    # Print Table
    print("\nFINAL RESULTS:")
    with open(results_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    run_benchmark()
