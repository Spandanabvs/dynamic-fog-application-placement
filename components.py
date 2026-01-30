import random
import itertools
import config


class Task:

    def __init__(self, task_id, creation_time, forced_task_type=None):
        self.task_id = task_id
        self.creation_time = creation_time
        self.cpu_required = random.uniform(config.TASK_CPU_REQUIREMENT[0], config.TASK_CPU_REQUIREMENT[1])
        
        if forced_task_type and forced_task_type in config.TASK_PROFILES:
            self.task_type = forced_task_type
        else:
            task_types = list(config.TASK_PROFILES.keys())
            probabilities = [config.TASK_PROFILES[t][0] for t in task_types]
            self.task_type = random.choices(task_types, weights=probabilities, k=1)[0]
            
        profile = config.TASK_PROFILES[self.task_type]
        self.data_size_mb = profile[1]
        self.deadline = profile[2]

    def __str__(self):
        return f'Task_{self.task_id} (Type: {self.task_type}, CPU: {self.cpu_required:.2f}, Data: {self.data_size_mb}MB)'


class IotDevice:

    def __init__(self, env, device_id, scheduler, results_collector, arrival_rate=None, forced_type=None):
        self.env = env
        self.device_id = device_id
        self.scheduler = scheduler
        self.results = results_collector
        self.arrival_rate = arrival_rate if arrival_rate is not None else config.TASK_ARRIVAL_RATE
        self.forced_type = forced_type
        self.task_counter = itertools.count()
        self.action = env.process(self.run(config.TASK_GENERATION_PERIOD))

    def run(self, generation_duration):
        # Check if this device has a specific configuration (legacy fallback)
        forced_type_runtime = config.IOT_DEVICE_CONFIG.get(self.device_id)
        
        # Priority: Constructor Argument > Legacy Dict Config > Random
        effective_task_type = self.forced_type if self.forced_type else forced_type_runtime
        if effective_task_type == "RANDOM": effective_task_type = None

        while self.env.now < generation_duration:
            interarrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(interarrival_time)
            if self.env.now >= generation_duration:
                break
            task_id = f'{self.device_id}-{next(self.task_counter)}'
            new_task = Task(task_id=task_id, creation_time=self.env.now, forced_task_type=effective_task_type)
            self.results.log_task_generation()
            print(f'[Time {self.env.now:.2f}] Device_{self.device_id}: Created {new_task}')
            self.scheduler.add_task(new_task)
        print(f'[Time {self.env.now:.2f}] Device_{self.device_id}: Stopping task generation.')
        self.results.log_generator_finished()
