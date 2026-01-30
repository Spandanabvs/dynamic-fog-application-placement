import simpy

class FogNode:

    def __init__(self, env, node_id, cpu_capacity, cpu_speed, power_idle, power_busy):
        self.env = env
        self.node_id = node_id
        self.cpu_speed = cpu_speed
        self.power_idle = power_idle
        self.power_busy = power_busy
        self.cpu = simpy.Resource(env, capacity=cpu_capacity)
        self.total_energy_consumed = 0.0
        self.tasks_processed = 0

    def get_cpu_load(self):
        return self.cpu.count / self.cpu.capacity

    def get_queue_length(self):
        return len(self.cpu.queue)

    def calculate_energy(self, processing_time):
        processing_time_seconds = processing_time / 1000.0
        energy = self.power_busy * processing_time_seconds
        self.total_energy_consumed += energy
        self.tasks_processed += 1
        return energy

    def __str__(self):
        return f'FogNode_{self.node_id}'

class CloudNode:

    def __init__(self, env, cpu_capacity, cpu_speed, power_idle, power_busy):
        self.env = env
        self.cpu_speed = cpu_speed
        self.power_idle = power_idle
        self.power_busy = power_busy
        self.cpu = simpy.Resource(env, capacity=cpu_capacity)
        self.total_energy_consumed = 0.0
        self.tasks_processed = 0

    def calculate_energy(self, processing_time):
        processing_time_seconds = processing_time / 1000.0
        energy = self.power_busy * processing_time_seconds
        self.total_energy_consumed += energy
        self.tasks_processed += 1
        return energy

    def get_cpu_load(self):
        return self.cpu.count / self.cpu.capacity

    def get_queue_length(self):
        return len(self.cpu.queue)

    def __str__(self):
        return 'CloudNode'