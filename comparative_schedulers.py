import random
import numpy as np
from firefly import calculate_precise_metrics

def normalize_metrics(latencies, energies):
    max_lat = np.max(latencies) if np.max(latencies) > 0 else 1
    max_eng = np.max(energies) if np.max(energies) > 0 else 1
    norm_lat = latencies / max_lat
    norm_eng = energies / max_eng
    return norm_lat, norm_eng

def run_halo_scheduler(task, fog_nodes, cloud_node):
    all_nodes = fog_nodes + [cloud_node]
    latencies, energies = calculate_precise_metrics(all_nodes, task)
    norm_lat, norm_eng = normalize_metrics(latencies, energies)
    
    w_lat = 0.2
    w_eng = 0.8
    fitness = (w_lat * norm_lat) + (w_eng * norm_eng)
    
    inv_fitness = 1.0 / (fitness + 1e-6)
    probs = inv_fitness / np.sum(inv_fitness)
    
    selected_index = np.random.choice(len(all_nodes), p=probs)
    best_index = np.argmin(fitness)
    
    if random.random() < 0.5:
        return all_nodes[best_index]
    else:
        return all_nodes[selected_index]

def run_mocs_scheduler(task, fog_nodes, cloud_node):
    all_nodes = fog_nodes + [cloud_node]
    latencies, energies = calculate_precise_metrics(all_nodes, task)
    norm_lat, norm_eng = normalize_metrics(latencies, energies)
    
    host_idx = random.randint(0, len(all_nodes) - 1)
    green_idx = np.argmin(energies)
    
    w_lat = 0.2
    w_eng = 0.8
    
    host_cost = (w_lat * norm_lat[host_idx]) + (w_eng * norm_eng[host_idx])
    cuckoo_cost = (w_lat * norm_lat[green_idx]) + (w_eng * norm_eng[green_idx])
    
    if cuckoo_cost < host_cost:
        return all_nodes[green_idx] 
    else:
        Pa = 0.25
        if random.random() < Pa:
            fast_idx = np.argmin(latencies)
            return all_nodes[fast_idx]
        else:
            return all_nodes[host_idx]

def run_spea2_scheduler(task, fog_nodes, cloud_node):
    all_nodes = fog_nodes + [cloud_node]
    latencies, energies = calculate_precise_metrics(all_nodes, task)
    
    num_nodes = len(all_nodes)
    dominated_count = np.zeros(num_nodes)
    
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i == j: continue
            if (latencies[j] <= latencies[i] and energies[j] <= energies[i]) and\
               (latencies[j] < latencies[i] or energies[j] < energies[i]):
                dominated_count[i] += 1
                
    pareto_indices = np.where(dominated_count == 0)[0]
    
    if len(pareto_indices) == 0:
        return all_nodes[np.argmin(latencies)]
        
    p_lat = latencies[pareto_indices]
    p_eng = energies[pareto_indices]
    
    max_p_lat = np.max(p_lat) if np.max(p_lat) > 0 else 1
    max_p_eng = np.max(p_eng) if np.max(p_eng) > 0 else 1
    
    norm_p_lat = p_lat / max_p_lat
    norm_p_eng = p_eng / max_p_eng
    
    distances = np.sqrt(0.2 * norm_p_lat**2 + 0.8 * norm_p_eng**2)
    
    valid_mask = p_lat <= task.deadline
    
    if np.any(valid_mask):
        valid_indices_in_subset = np.where(valid_mask)[0]
        best_in_subset = valid_indices_in_subset[np.argmin(distances[valid_indices_in_subset])]
        best_global_index = pareto_indices[best_in_subset]
    else:
        best_in_subset = np.argmin(distances)
        best_global_index = pareto_indices[best_in_subset]
        
    return all_nodes[best_global_index]
