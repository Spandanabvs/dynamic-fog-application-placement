import simpy
import random
import config
from network import get_iot_to_fog_latency, get_fog_to_cloud_latency
from hybrid_logic import run_hybrid_logic, update_agent, agent
from comparative_schedulers import run_spea2_scheduler, run_mocs_scheduler
from logger import log_task_assignment, log_task_completion

def shortest_queue_logic(task, fog_nodes, cloud_node):
    all_nodes = fog_nodes + [cloud_node]
    best_node = min(all_nodes, key=lambda node: node.get_queue_length())
    return best_node

def hybrid_scheduler_logic(task, fog_nodes, cloud_node, current_time):
    return run_hybrid_logic(task, fog_nodes, cloud_node, current_time)

def round_robin_logic(task, fog_nodes, cloud_node, last_node_index):
    node_index = (last_node_index + 1) % len(fog_nodes)
    best_node = fog_nodes[node_index]
    return (best_node, node_index)

def random_logic(task, fog_nodes, cloud_node):
    best_node = random.choice(fog_nodes)
    return best_node

class Scheduler:

    def __init__(self, env, fog_nodes, cloud_node, results_collector):
        self.env = env
        self.fog_nodes = fog_nodes
        self.cloud_node = cloud_node
        self.results = results_collector
        self.task_queue = simpy.Store(env)
        self.strategy = config.SCHEDULER_TYPE
        self.round_robin_index = -1
        self.action = env.process(self.run())

    def add_task(self, task):
        self.task_queue.put(task)

    def run(self):
        print(f"[Scheduler]: Started with '{self.strategy}' strategy.")
        while True:
            task = (yield self.task_queue.get())
            weights = None
            if self.strategy == 'HYBRID':
                best_node, weights = hybrid_scheduler_logic(task, self.fog_nodes, self.cloud_node, self.env.now)
            elif self.strategy == 'SHORTEST_QUEUE':
                best_node = shortest_queue_logic(task, self.fog_nodes, self.cloud_node)
            elif self.strategy == 'ROUND_ROBIN':
                best_node, self.round_robin_index = round_robin_logic(task, self.fog_nodes, self.cloud_node, self.round_robin_index)
            elif self.strategy == 'RANDOM':
                best_node = random_logic(task, self.fog_nodes, self.cloud_node)
            elif self.strategy == 'SPEA2':
                best_node = run_spea2_scheduler(task, self.fog_nodes, self.cloud_node)
            elif self.strategy == 'MOCS':
                best_node = run_mocs_scheduler(task, self.fog_nodes, self.cloud_node)
            else:
                print(f"ERROR: Unknown strategy '{self.strategy}'")
                best_node = self.fog_nodes[0]

            node_queue_at_dispatch = best_node.get_queue_length()
            node_load_at_dispatch = best_node.get_cpu_load()
            log_task_assignment(self.env.now, task, best_node)
            self.env.process(self.execute_task_on_node(task, best_node, node_queue_at_dispatch, node_load_at_dispatch))

    def execute_task_on_node(self, task, node, node_queue_at_dispatch, node_load_at_dispatch):
        if node == self.cloud_node:
            latency = get_iot_to_fog_latency() + get_fog_to_cloud_latency()
        else:
            latency = get_iot_to_fog_latency()

        data_size_mbits = task.data_size_mb * 8
        transfer_time_sec = data_size_mbits / config.NETWORK_BANDWIDTH_MBPS
        transfer_time_ms = transfer_time_sec * 1000
        yield self.env.timeout(latency + transfer_time_ms)

        arrival_at_node = self.env.now
        with node.cpu.request() as req:
            yield req
            start_processing = self.env.now
            waiting_time = start_processing - arrival_at_node

            proc_time_ms = task.cpu_required / node.cpu_speed * 1000
            yield self.env.timeout(proc_time_ms)
            completion_time = self.env.now
            energy = node.calculate_energy(proc_time_ms)
            final_latency = completion_time - task.creation_time
            
            self.results.log_task_completion(
                task_id=task.task_id, 
                task_type=task.task_type, 
                task_cpu_required=task.cpu_required, 
                task_data_size_mb=task.data_size_mb, 
                deadline=task.deadline, 
                node_id=str(node), 
                node_queue_at_dispatch=node_queue_at_dispatch, 
                node_load_at_dispatch=node_load_at_dispatch, 
                node_cpu_speed=node.cpu_speed, 
                creation_time=task.creation_time, 
                completion_time=completion_time, 
                latency=final_latency, 
                waiting_time=waiting_time, 
                energy_consumed=energy, 
                predicted_latency=None, 
                predicted_energy=None
            )
            log_task_completion(self.env.now, task, node, final_latency)

                            
            if self.strategy == 'HYBRID':
                                    
                reward = 0
                if final_latency <= task.deadline:
                    reward += 10
                    if final_latency < task.deadline * 0.5:
                        reward += 5                  
                else:
                    reward -= 10                               
                
                                                     
                reward -= (energy * 0.1)

                                                  
                                                                                  
                from hybrid_logic import history_window
                history_window.append(0 if final_latency <= task.deadline else 1)
                if len(history_window) > 50: history_window.pop(0)
                
                all_nodes = self.fog_nodes + [self.cloud_node]
                avg_q = sum(n.get_queue_length() for n in all_nodes) / len(all_nodes)
                miss_rate = sum(history_window) / len(history_window)

                update_agent(reward, avg_q, miss_rate)