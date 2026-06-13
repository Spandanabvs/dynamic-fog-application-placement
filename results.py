import pandas as pd
import os

class ResultsCollector:

    def __init__(self):
        self.log = []
        self.tasks_generated = 0
        self.tasks_completed = 0
        self.generators_finished = 0
        self.avg_latency = 0
        self.total_energy = 0

    def log_task_generation(self):
        self.tasks_generated += 1

    def log_generator_finished(self):
        self.generators_finished += 1

    def all_generators_done(self, num_generators):
        return self.generators_finished == num_generators

    def all_tasks_done(self):
        return self.tasks_completed == self.tasks_generated and self.tasks_completed > 0

    def get_dataframe(self):
        return pd.DataFrame(self.log)

    def save_to_csv(self, filename='task_data.csv'):
        if not self.log: return
        self.get_dataframe().to_csv(filename, index=False)
        print(f'Results saved to {filename}')

    def log_task_completion(self, **kwargs):
        self.log.append(kwargs)
        self.tasks_completed += 1

    def calculate_average_latency(self):
        if not self.log: return 0
        df = self.get_dataframe()
        self.avg_latency = df['latency'].mean()
        return self.avg_latency

    def calculate_total_energy(self):
        if not self.log: return 0
        df = self.get_dataframe()
        self.total_energy = df['energy_consumed'].sum()
        return self.total_energy

    def print_summary(self):
        if not self.log:
            print('No tasks were completed.')
            return
        df = self.get_dataframe()
        avg_waiting = df['waiting_time'].mean() if 'waiting_time' in df.columns else 0.0
        
                           
        if self.avg_latency == 0: self.calculate_average_latency()
        if self.total_energy == 0: self.calculate_total_energy()

        print(f'\n--- Final Results ---')
        print(f'   Total Tasks Generated: {self.tasks_generated}')
        print(f'   Total Tasks Completed: {len(df)}')
        print(f'   Average Latency: {self.avg_latency:.4f} ms')
        print(f'   Average Waiting Time: {avg_waiting:.4f} ms')
        print(f'   Total Energy Consumed: {self.total_energy:.4f} Joules')
        print('-------------------------')

    def append_benchmark_result(self, filename='benchmark_results.csv', scheduler_name='UNKNOWN'):
        if self.avg_latency == 0: self.calculate_average_latency()
        if self.total_energy == 0: self.calculate_total_energy()
        
        df = self.get_dataframe()
        
                                      
        miss_count = 0
        if not df.empty and 'deadline' in df.columns and 'latency' in df.columns:
            miss_count = df[df['latency'] > df['deadline']].shape[0]
        miss_rate = miss_count / len(df) if not df.empty else 0.0

                              
        throughput = 0.0
        if not df.empty and 'completion_time' in df.columns and 'creation_time' in df.columns:
            duration = df['completion_time'].max() - df['creation_time'].min()
            if duration > 0:
                throughput = len(df) / duration

                                        
        q_size = 0
        epsilon = 0.0
        if scheduler_name == 'HYBRID':
            try:
                from hybrid_logic import agent
                q_size = len(agent.q_table)
                epsilon = agent.epsilon
            except ImportError:
                pass

        file_exists = os.path.isfile(filename)
        
        import csv
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Scheduler', 'AverageLatency', 'TotalEnergy', 'TasksCompleted', 'DeadlineMissRate', 'Throughput', 'QTableSize', 'Epsilon'])
            writer.writerow([scheduler_name, self.avg_latency, self.total_energy, self.tasks_completed, miss_rate, throughput, q_size, epsilon])
        print(f"   [+] Benchmark result appended to {filename}")