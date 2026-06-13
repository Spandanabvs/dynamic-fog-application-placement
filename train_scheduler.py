import config
import time
import sys
import os
from main import run_simulation
from hybrid_logic import agent

                                    
class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def train_agent(epochs=50):
    print(f"--- 🏋️ Beginning Training for {epochs} Epochs (Silent Mode) ---")
    
    config.SCHEDULER_TYPE = 'HYBRID'
    config.TRAINING_MODE = True
    config.BENCHMARK_MODE = False
    
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        
                                               
        with SuppressStdout():
            results = run_simulation(training_mode=True)
        
                                 
        q_len = len(agent.q_table)
        epsilon = agent.epsilon
        
                                           
        print(f"[Epoch {epoch}/{epochs}] Latency: {results.avg_latency:.2f}ms | Energy: {results.total_energy:.2f}J | Q-Table: {q_len} | Eps: {epsilon:.4f}")
        
    total_time = time.time() - start_time
    print(f"\n--- 🏁 Training Finished in {total_time:.2f}s ---")
    print("Final Q-Table saved to q_table.pkl")

if __name__ == "__main__":
    train_agent(epochs=50)
