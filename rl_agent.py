import numpy as np
import random
import pickle
import os

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.actions = actions                                                         
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = {} 
        self.last_state = None
        self.last_action_index = None

                                      
        self.load_q_table()

    def get_state_key(self, avg_queue_length, recent_deadline_miss_rate):
                     
        if avg_queue_length < 5: q_state = "LOW_Q"
        elif avg_queue_length < 20: q_state = "MED_Q"
        else: q_state = "HIGH_Q"

                        
        if recent_deadline_miss_rate < 0.05: d_state = "SAFE"
        elif recent_deadline_miss_rate < 0.20: d_state = "RISKY"
        else: d_state = "CRITICAL"

        return (q_state, d_state)

    def choose_action(self, state, training=True):
        self.last_state = state
        
                                            
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions))

                                 
        if training and random.random() < self.epsilon:
            action_index = random.randint(0, len(self.actions) - 1)
        else:
            action_index = np.argmax(self.q_table[state])
        
        self.last_action_index = action_index
        return self.actions[action_index]

    def learn(self, reward, next_state):
        if self.last_state is None or self.last_action_index is None:
            return

        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(len(self.actions))

        old_value = self.q_table[self.last_state][self.last_action_index]
        next_max = np.max(self.q_table[next_state])

                            
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[self.last_state][self.last_action_index] = new_value

                       
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, filename="q_table.pkl"):
        try:
            with open(filename, "wb") as f:
                pickle.dump(self.q_table, f)
                                                                     
        except Exception as e:
            print(f"Error saving Q-Table: {e}")

    def load_q_table(self, filename="q_table.pkl"):
        if os.path.exists(filename):
            try:
                with open(filename, "rb") as f:
                    self.q_table = pickle.load(f)
                print("Loaded existing Q-Table.")
            except Exception:
                print("Could not load Q-Table, starting fresh.")
