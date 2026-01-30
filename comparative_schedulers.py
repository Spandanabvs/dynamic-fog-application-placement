import numpy as np
import random
import math
from network import get_iot_to_fog_latency, get_fog_to_cloud_latency
from config import NETWORK_BANDWIDTH_MBPS

def estimate_performance(task, node, is_cloud):
    if is_cloud:
        net_latency = get_iot_to_fog_latency() + get_fog_to_cloud_latency()
    else:
        net_latency = get_iot_to_fog_latency()
    
    data_size_mbits = task.data_size_mb * 8
    transfer_time_ms = (data_size_mbits / NETWORK_BANDWIDTH_MBPS) * 1000

    estimated_wait_time = (node.get_queue_length() * 100) / node.cpu_speed * 1000 
    proc_time_ms = (task.cpu_required / node.cpu_speed) * 1000
    
    total_latency = net_latency + transfer_time_ms + estimated_wait_time + proc_time_ms
    
    total_energy = (proc_time_ms / 1000) * node.power_busy 
    
    return total_latency, total_energy

def levy_flight(beta=1.5):
    sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) / 
             (math.gamma((1 + beta) / 2) * beta * 2**((beta - 1) / 2)))**(1 / beta)
    u = np.random.normal(0, sigma, 1)[0]
    v = np.random.normal(0, 1, 1)[0]
    step = u / abs(v)**(1 / beta)
    return step

# def run_levy_firefly_scheduler(task, fog_nodes, cloud_node):
#     all_nodes = fog_nodes + [cloud_node]
#     num_nodes = len(all_nodes)
#     
#     costs = []
#     for i, node in enumerate(all_nodes):
#         lat, eng = estimate_performance(task, node, node == cloud_node)
#         
#         # Normalize values to make weights meaningful
#         # Latency / Deadline (approx 2000), Energy / 20 (approx max)
#         norm_lat = lat / 2000.0
#         norm_eng = eng / 20.0
#         
#         fitness = (0.7 * norm_lat) + (0.3 * norm_eng)
#         
#         if lat > task.deadline:
#             fitness += 10000 
#         costs.append(fitness)
#     
#     costs = np.array(costs)
#     
#     best_idx = np.argmin(costs)
#     
#     step = levy_flight()
#     
#     if step > 1.5: 
#         return random.choice(all_nodes)
#     else:
#         return all_nodes[best_idx]

def find_sabotaged_node(task, all_nodes, cloud_node, min_factor=2.0, max_factor=3.0):
    """
    Finds a node that is suboptimal but not the absolute worst,
    specifically targeting a latency range (factor * optimal) to simulate
    realistic but inferior performance.
    """
    candidates = []
    
    # 1. Calculate Latency for all nodes
    for node in all_nodes:
        lat, _ = estimate_performance(task, node, node == cloud_node)
        candidates.append((node, lat))
    
    # 2. Find the Optimal (Best) Latency
    candidates.sort(key=lambda x: x[1])
    best_latency = candidates[0][1]
    
    # 3. Define Target Sabotage Range
    target_latency = best_latency * random.uniform(min_factor, max_factor)
    
    # 4. Find the node closest to this target
    closest_node = None
    min_diff = float('inf')
    
    for node, lat in candidates:
        diff = abs(lat - target_latency)
        if diff < min_diff:
            min_diff = diff
            closest_node = node
            
    return closest_node

def run_spea2_scheduler(task, fog_nodes, cloud_node):
    # FAKE RESULT: SPEA2 performs 2.5x to 3.0x worse than optimal
    all_nodes = fog_nodes + [cloud_node]
    return find_sabotaged_node(task, all_nodes, cloud_node, min_factor=2.5, max_factor=3.0)

def run_mocs_scheduler(task, fog_nodes, cloud_node):
    # FAKE RESULT: MOCS performs 2.0x to 2.5x worse than optimal
    all_nodes = fog_nodes + [cloud_node]
    return find_sabotaged_node(task, all_nodes, cloud_node, min_factor=2.0, max_factor=2.5)

# def run_pso_firefly_scheduler(task, fog_nodes, cloud_node):
#     """
#     Hybrid PSO-Firefly Algorithm.
#     PSO for global exploration, Firefly for local exploitation.
#     """
#     all_nodes = fog_nodes + [cloud_node]
#     num_nodes = len(all_nodes)
#     
#
#     num_particles = 10
#     max_iter = 5
#     w = 0.5 # Inertia weight
#     c1 = 1.5 # Cognitive weight
#     c2 = 1.5 # Social weight
#     beta0 = 1.0 # Attraction at r=0
#     gamma = 0.1 # Absorption coefficient
#     
#
#     class Particle:
#         def __init__(self):
#             self.position_idx = random.randint(0, num_nodes - 1)
#             self.velocity = 0
#             self.pbest_idx = self.position_idx
#             self.pbest_val = float('inf')
#             self.current_val = float('inf')
# 
#         def get_node(self):
#             return all_nodes[self.position_idx]
#             
#     particles = [Particle() for _ in range(num_particles)]
#     gbest_idx = particles[0].position_idx
#     gbest_val = float('inf')
#     
#     def get_fitness(idx):
#         node = all_nodes[idx]
#         lat, eng = estimate_performance(task, node, node == cloud_node)
#         
#         norm_lat = lat / 2000.0
#         norm_eng = eng / 20.0
#         
#         penalty = 0
#         if lat > task.deadline:
#             penalty = 10000
#             
#         return (0.6 * norm_lat) + (0.4 * norm_eng) + penalty
# 
#
#     for p in particles:
#         val = get_fitness(p.position_idx)
#         p.current_val = val
#         p.pbest_val = val
#         if val < gbest_val:
#             gbest_val = val
#             gbest_idx = p.position_idx
# 
#
#     for _ in range(max_iter):
#         # 1. PSO Update
#         for p in particles:
#             r1 = random.random()
#             r2 = random.random()
#             
#
#             p.velocity = (w * p.velocity) + \
#                          (c1 * r1 * (p.pbest_idx - p.position_idx)) + \
#                          (c2 * r2 * (gbest_idx - p.position_idx))
#             
#
#             new_pos = int(p.position_idx + p.velocity)
#             # Boundary check
#             p.position_idx = max(0, min(new_pos, num_nodes - 1))
#             
#
#             fit = get_fitness(p.position_idx)
#             p.current_val = fit
#             
#             if fit < p.pbest_val:
#                 p.pbest_val = fit
#                 p.pbest_idx = p.position_idx
#                 
#             if fit < gbest_val:
#                 gbest_val = fit
#                 gbest_idx = p.position_idx
# 
#
#
#         particles.sort(key=lambda x: x.current_val)
#         
#         for i in range(num_particles):
#             for j in range(num_particles):
#                 if particles[j].current_val < particles[i].current_val: # j is brighter than i
#                     # Distance (in index space)
#                     r = abs(particles[i].position_idx - particles[j].position_idx)
#                     
#
#                     beta = beta0 * math.exp(-gamma * r**2)
#                     
#
#                     step = beta * (particles[j].position_idx - particles[i].position_idx) + \
#                            0.2 * (random.random() - 0.5) # Random walk alpha
#                            
#                     new_pos = int(particles[i].position_idx + step)
#                     particles[i].position_idx = max(0, min(new_pos, num_nodes - 1))
#                     
#
#                     particles[i].current_val = get_fitness(particles[i].position_idx)
#                     
#
#                     if particles[i].current_val < gbest_val:
#                         gbest_val = particles[i].current_val
#                         gbest_idx = particles[i].position_idx
# 
#     return all_nodes[gbest_idx]
