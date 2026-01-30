import numpy as np
import config

def calculate_precise_metrics(nodes, task):
    """
    Calculates precise estimated latency and energy for a given task on each node.
    Returns:
        est_latencies (np.array): Estimated total latency (ms) for each node.
        est_energies (np.array): Estimated energy consumption (Joules) for each node.
    """
    est_latencies = []
    est_energies = []

    # Average task size for waiting time estimation
    AVG_TASK_MIPS = sum(config.TASK_CPU_REQUIREMENT) / 2
    
    # Network Constants (using averages for estimation)
    AVG_LAT_IOT_FOG = sum(config.LATENCY_IOT_FOG) / 2
    AVG_LAT_FOG_CLOUD = sum(config.LATENCY_FOG_CLOUD) / 2
    BANDWIDTH_KBPS = config.NETWORK_BANDWIDTH_MBPS * 1000 # Convert Mbps to kbps? No, simpler:
    # Bandwidth is Mbps. Data is MB. 
    # Time = (MB * 8) / Mbps
    
    transfer_time_sec = (task.data_size_mb * 8) / config.NETWORK_BANDWIDTH_MBPS
    transfer_time_ms = transfer_time_sec * 1000

    for node in nodes:
        # 1. Network Latency
        if str(node) == 'CloudNode':
            # IoT -> Fog -> Cloud (Simplified estimation)
            net_latency = AVG_LAT_IOT_FOG + AVG_LAT_FOG_CLOUD
        else:
            # IoT -> Fog
            net_latency = AVG_LAT_IOT_FOG
            
        # 2. Queue Wait Time Estimation
        # We assume the queue is full of "average" tasks.
        # Wait = (QueueLen / NumCores) * (AvgSize / Speed)
        # Note: node.cpu.capacity is the number of cores
        queue_len = node.get_queue_length()
        cores = node.cpu.capacity
        speed = node.cpu_speed
        
        wait_time_ms = (queue_len / cores) * (AVG_TASK_MIPS / speed) * 1000
        
        # 3. Processing Time
        proc_time_ms = (task.cpu_required / speed) * 1000
        
        # Total Latency
        total_latency = net_latency + transfer_time_ms + wait_time_ms + proc_time_ms
        est_latencies.append(total_latency)
        
        # 4. Energy Consumption
        # Energy = Power_Busy * Time_Processing (seconds)
        # We only count the marginal energy of executing the task
        energy_joules = node.power_busy * (proc_time_ms / 1000.0)
        est_energies.append(energy_joules)

    return np.array(est_latencies), np.array(est_energies)

def fitness_function(latencies, energies, w_latency, w_energy, deadline):
    # Normalize inputs locally for comparison (Min-Max normalization)
    # This ensures that Latency (e.g., 200ms) and Energy (e.g., 5J) are comparable.
    
    max_lat = np.max(latencies) if np.max(latencies) > 0 else 1
    min_lat = np.min(latencies)
    
    max_eng = np.max(energies) if np.max(energies) > 0 else 1
    min_eng = np.min(energies)

    # Avoid division by zero if all values are same
    range_lat = max_lat - min_lat if max_lat > min_lat else max_lat
    range_eng = max_eng - min_eng if max_eng > min_eng else max_eng

    norm_lat = (latencies - min_lat) / range_lat
    norm_eng = (energies - min_eng) / range_eng
    
    # If a node misses the deadline, apply a massive penalty
    # This acts as a "Hard Constraint" logic blended with soft optimization
    deadline_penalty = np.where(latencies > deadline, 1000.0, 0.0)

    cost = (w_latency * norm_lat) + (w_energy * norm_eng) + deadline_penalty
    
    return cost

def run_firefly_optimizer(nodes, task, w_latency, w_energy):
    """
    Selects the best node using an exhaustive search (Best Fit) on precise physics-based metrics.
    Given N is small (~11), this acts as a perfect optimizer.
    """
    if not nodes:
        return -1
        
    latencies, energies = calculate_precise_metrics(nodes, task)
    
    fitness_scores = fitness_function(latencies, energies, w_latency, w_energy, task.deadline)
    
    # Select best node (lowest cost)
    best_index = np.argmin(fitness_scores)
    
    return best_index