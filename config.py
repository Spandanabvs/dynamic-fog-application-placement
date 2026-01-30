
# Number of IoT devices that will generate tasks.
NUM_IOT_DEVICES = 10
# The rate at which each IoT device generates tasks (tasks per second).
TASK_ARRIVAL_RATE = 0.5
# The range of CPU instructions required by a task (in MIPS).
TASK_CPU_REQUIREMENT = [50, 1000]
# The time period (in virtual seconds) during which tasks are generated.
TASK_GENERATION_PERIOD = 100

# Number of fog nodes in the environment.
NUM_FOG_NODES = 10
# The range of CPU cores for each fog node.
FOG_CPU_CAPACITY_RANGE = [2, 8]
# The range of CPU processing speed for each fog node (in MIPS).
FOG_CPU_SPEED_RANGE = [500, 2000]
# The range of power consumption for an idle fog node (in Watts).
FOG_POWER_IDLE_RANGE = [30, 80]
# The range of power consumption for a busy fog node (in Watts).
FOG_POWER_BUSY_RANGE = [60, 150]

# Number of CPU cores for the cloud server.
CLOUD_CPU_CAPACITY = 24
# CPU processing speed for the cloud server (in MIPS).
CLOUD_CPU_SPEED = 12000
# Power consumption for the idle cloud server (in Watts).
CLOUD_POWER_IDLE = 200
# Power consumption for the busy cloud server (in Watts).
CLOUD_POWER_BUSY = 500

# Network latency range from an IoT device to a fog node (in milliseconds).
LATENCY_IOT_FOG = [5, 15]
# Network latency range from a fog node to the cloud (in milliseconds).
LATENCY_FOG_CLOUD = [50, 100]
# The network bandwidth available for data transmission (in Megabits per second).
NETWORK_BANDWIDTH_MBPS = 100

# Defines different types of tasks. Each entry is a tuple containing:
# (generation_probability, data_size_in_MB, deadline_in_ms)
TASK_PROFILES = {
    'AUGMENTED_REALITY': (0.05, 30, 150),
    'HEALTH_MONITORING': (0.15, 1, 100),
    'VIDEO_SURVEILLANCE': (0.05, 60, 800),
    'GPS_TRACKING': (0.15, 0.2, 200),
    'SENSOR_DATA_LOGGING': (0.2, 0.1, 10000),
    'VOICE_ASSISTANT': (0.1, 2, 150),
    'CLOUD_GAMING': (0.05, 50, 150),
    'E_COMMERCE_TRANSACTION': (0.1, 0.5, 300),
    'SMART_HOME_CONTROL': (0.1, 0.1, 150),
    'BATCH_DATA_PROCESSING': (0.05, 200, 30000)
}

# The scheduling algorithm to be used: "HYBRID", "ROUND_ROBIN", "RANDOM", "SHORTEST_QUEUE", "SPEA2", "MOCS"
SCHEDULER_TYPE = 'HYBRID'

# Fog Node Configuration Mode: "RANDOM", "HIGH_PERFORMANCE", "LOW_POWER", "MIXED"
FOG_CONFIG_MODE = "RANDOM"

# Presets for Fog Node Generations
FOG_CONFIG_PRESETS = {
    "RANDOM": {
        "FOG_CPU_CAPACITY_RANGE": [2, 8],
        "FOG_CPU_SPEED_RANGE": [500, 2000],
        "FOG_POWER_IDLE_RANGE": [30, 80],
        "FOG_POWER_BUSY_RANGE": [60, 150]
    },
    "HIGH_PERFORMANCE": {
        "FOG_CPU_CAPACITY_RANGE": [8, 16],
        "FOG_CPU_SPEED_RANGE": [2000, 4000],
        "FOG_POWER_IDLE_RANGE": [80, 120],
        "FOG_POWER_BUSY_RANGE": [150, 250]
    },
    "LOW_POWER": {
        "FOG_CPU_CAPACITY_RANGE": [1, 4],
        "FOG_CPU_SPEED_RANGE": [300, 1000],
        "FOG_POWER_IDLE_RANGE": [10, 30],
        "FOG_POWER_BUSY_RANGE": [30, 60]
    },
    "MIXED": {
        "FOG_CPU_CAPACITY_RANGE": [2, 12],
        "FOG_CPU_SPEED_RANGE": [500, 3000],
        "FOG_POWER_IDLE_RANGE": [20, 100],
        "FOG_POWER_BUSY_RANGE": [50, 200]
    }
}

# Configuration for IoT Devices: mapping device_id (int) to task_type (str)
# If empty or device_id not found, defaults to random generation based on TASK_PROFILES.
# Example: {0: 'VIDEO_SURVEILLANCE', 1: 'HEALTH_MONITORING'}
IOT_DEVICE_CONFIG = {}

# Custom Fog Node Configuration (List of Dicts)
# If populated, this overrides NUM_FOG_NODES and FOG_CONFIG_MODE.
# Example: [{'node_id': 0, 'cpu_capacity': 4, 'cpu_speed': 1200, 'power_idle': 50, 'power_busy': 100}, ...]
FOG_NODES_CUSTOM_CONFIG = []

# Custom IoT Device Configuration (List of Dicts)
# If populated, this overrides NUM_IOT_DEVICES.
# Example: [{'device_id': 0, 'task_type': 'VIDEO_SURVEILLANCE', 'arrival_rate': 0.5}, ...]
IOT_DEVICES_CUSTOM_CONFIG = []

# Logging Configuration
LOG_LEVEL = "ERROR"
LOG_INTERVAL = 20

# Simulation Modes
TRAINING_MODE = False
BENCHMARK_MODE = False
