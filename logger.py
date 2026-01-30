from datetime import datetime

def log_task_assignment(time, task, node):
    print(f'[Time {time:.2f}] {task.task_id} assigned to {node}')

def log_task_completion(time, task, node, latency):
    print(f'[Time {time:.2f}] {task.task_id} completed on {node}')