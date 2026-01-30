import simpy
import random
import config
import argparse
from environment import FogNode, CloudNode
from components import IotDevice
from scheduler import Scheduler
from results import ResultsCollector

def simulation_controller(env, results_collector):
    while not results_collector.all_generators_done(config.NUM_IOT_DEVICES):
        yield env.timeout(10)
    print(f'\n[Time {env.now:.2f}] --- All Task Generators Finished. ---')
    print(f'[Time {env.now:.2f}] --- Total Tasks Generated: {results_collector.tasks_generated} ---')
    print(f'[Time {env.now:.2f}] --- Waiting for tasks to complete... ---')
    while not results_collector.all_tasks_done():
        print(
            f'[Time {env.now:.2f}] ... waiting ... ({results_collector.tasks_completed} / {results_collector.tasks_generated})')
        yield env.timeout(20)
    print(f'\n[Time {env.now:.2f}] --- ALL {results_collector.tasks_completed} TASKS COMPLETED ---')


def run_simulation(training_mode=False, benchmark_mode=False):
    print('--- Initializing Fog-Cloud Simulation ---')
    
    config.TRAINING_MODE = training_mode
    config.BENCHMARK_MODE = benchmark_mode

    if training_mode:
        print("   [!] TRAINING MODE ENABLED")
        config.TASK_GENERATION_PERIOD = 2000 
    elif benchmark_mode:
        config.TASK_GENERATION_PERIOD = 1000 
    
    env = simpy.Environment()
    results = ResultsCollector();
    print('   [+] Created Results Collector')

    # Load Fog Configuration based on Mode
    fog_nodes = []
    
    if config.FOG_NODES_CUSTOM_CONFIG:
        print(f'   [+] Using Custom Fog Node Configuration with {len(config.FOG_NODES_CUSTOM_CONFIG)} nodes.')
        config.NUM_FOG_NODES = len(config.FOG_NODES_CUSTOM_CONFIG) # Sync global count
        
        for node_conf in config.FOG_NODES_CUSTOM_CONFIG:
             node = FogNode(env=env, 
                            node_id=node_conf['node_id'],
                            cpu_capacity=node_conf['cpu_capacity'],
                            cpu_speed=node_conf['cpu_speed'],
                            power_idle=node_conf['power_idle'],
                            power_busy=node_conf['power_busy'])
             fog_nodes.append(node)
    else:
        fog_preset = config.FOG_CONFIG_PRESETS.get(config.FOG_CONFIG_MODE, config.FOG_CONFIG_PRESETS["RANDOM"])
        print(f'   [+] Fog Config Mode: {config.FOG_CONFIG_MODE}')

        for i in range(config.NUM_FOG_NODES):
            node = FogNode(env=env, node_id=i,
                           cpu_capacity=random.randint(fog_preset["FOG_CPU_CAPACITY_RANGE"][0], fog_preset["FOG_CPU_CAPACITY_RANGE"][1]),
                           cpu_speed=random.uniform(fog_preset["FOG_CPU_SPEED_RANGE"][0], fog_preset["FOG_CPU_SPEED_RANGE"][1]),
                           power_idle=random.uniform(fog_preset["FOG_POWER_IDLE_RANGE"][0], fog_preset["FOG_POWER_IDLE_RANGE"][1]),
                           power_busy=random.uniform(fog_preset["FOG_POWER_BUSY_RANGE"][0], fog_preset["FOG_POWER_BUSY_RANGE"][1]))
            fog_nodes.append(node)

    # Save Fog Node Config to CSV
    import csv
    with open('fog_node_config.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['NodeID', 'CPUCapacity', 'CPUSpeed', 'PowerIdle', 'PowerBusy'])
        for node in fog_nodes:
            writer.writerow([node.node_id, node.cpu.capacity, node.cpu_speed, node.power_idle, node.power_busy])

    print(f'   [+] Created {len(fog_nodes)} Fog Nodes and saved config to fog_node_config.csv')

    cloud_node = CloudNode(env=env, cpu_capacity=config.CLOUD_CPU_CAPACITY, cpu_speed=config.CLOUD_CPU_SPEED,
                           power_idle=config.CLOUD_POWER_IDLE, power_busy=config.CLOUD_POWER_BUSY)
    print(f'   [+] Created {cloud_node}')

    scheduler = Scheduler(env, fog_nodes, cloud_node, results)

    iot_devices = []
    
    if config.IOT_DEVICES_CUSTOM_CONFIG:
        print(f'   [+] Using Custom IoT Device Configuration with {len(config.IOT_DEVICES_CUSTOM_CONFIG)} devices.')
        config.NUM_IOT_DEVICES = len(config.IOT_DEVICES_CUSTOM_CONFIG) # Sync global count
        
        for device_conf in config.IOT_DEVICES_CUSTOM_CONFIG:
            device = IotDevice(env=env, 
                               device_id=device_conf['device_id'], 
                               scheduler=scheduler, 
                               results_collector=results,
                               arrival_rate=device_conf.get('arrival_rate'),
                               forced_type=device_conf.get('task_type'))
            iot_devices.append(device)
    else:
        for i in range(config.NUM_IOT_DEVICES):
            device = IotDevice(env=env, device_id=i, scheduler=scheduler, results_collector=results)
            iot_devices.append(device)

    print(f'   [+] Created {len(iot_devices)} IoT Devices')
    print(f'\n---  Starting Simulation (Strategy: {config.SCHEDULER_TYPE}, Gen Period: {config.TASK_GENERATION_PERIOD}s) ---')
    controller_proc = env.process(simulation_controller(env, results))
    env.run(until=controller_proc)

    print(f'\n--- Simulation Finished at time {env.now} ---')
    print("Simulation finished.")
    print("Generating results...")
    
    if config.SCHEDULER_TYPE == 'HYBRID':
        from hybrid_logic import agent
        agent.save_q_table()
        print(f"RL Agent Q-Table saved. Size: {len(agent.q_table)} states.")

    results.calculate_average_latency()
    results.calculate_total_energy()
    results.print_summary()
    results.save_to_csv('task_data.csv')
    
    if config.BENCHMARK_MODE:
        results.append_benchmark_result('benchmark_results.csv', config.SCHEDULER_TYPE)
        
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fog-Cloud Simulation')
    parser.add_argument('--scheduler', type=str, help='Scheduler Type (HYBRID, ROUND_ROBIN, etc.)')
    parser.add_argument('--train', action='store_true', help='Enable Training Mode (Longer run, explores more)')
    parser.add_argument('--benchmark', action='store_true', help='Enable Benchmark Mode (Append results to csv)')
    
    args = parser.parse_args()
    
    if args.scheduler:
        config.SCHEDULER_TYPE = args.scheduler.upper()
    
    run_simulation(training_mode=args.train, benchmark_mode=args.benchmark)
