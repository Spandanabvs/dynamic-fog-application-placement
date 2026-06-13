from rl_agent import QLearningAgent
from firefly import run_firefly_optimizer
import numpy as np
import config

                                                       
                                        
                               
                                         
ACTIONS = [
    (0.1, 0.9),
    (0.5, 0.5),
    (0.9, 0.1)
]

                         
agent = QLearningAgent(actions=ACTIONS)

                            
history_window = []
WINDOW_SIZE = 50

def run_hybrid_logic(task, fog_nodes, cloud_node, current_sim_time):
    global agent, history_window
    
    all_nodes = fog_nodes + [cloud_node]
    
                      
    avg_queue = sum(n.get_queue_length() for n in all_nodes) / len(all_nodes)
    miss_rate = sum(history_window) / len(history_window) if history_window else 0
    
    state = agent.get_state_key(avg_queue, miss_rate)
    
                                
                                                                    
    is_training = getattr(config, 'TRAINING_MODE', False)
    w_lat, w_eng = agent.choose_action(state, training=is_training)
    
                                        
    best_node_index = run_firefly_optimizer(all_nodes, task, w_lat, w_eng)
    best_node = all_nodes[best_node_index]
    
    return best_node, (w_lat, w_eng) 

def update_agent(reward, next_avg_queue, next_miss_rate):
    next_state = agent.get_state_key(next_avg_queue, next_miss_rate)
    agent.learn(reward, next_state)
