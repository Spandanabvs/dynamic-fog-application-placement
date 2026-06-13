import streamlit as st
import pandas as pd
import plotly.express as px
import config
import main
import time
import os
from run_benchmark import run_benchmark

                     
st.set_page_config(
    page_title="Fog-Cloud Simulator",
    layout="wide"
)

st.title("Application Placement In Fog Environment")

             
tab1, tab2 = st.tabs(["Single Simulation", "Benchmark"])

                                            
                          
                                            
with tab1:
                                      
    st.sidebar.header("1. Configuration")

                                       
    scheduler_type = st.sidebar.selectbox(
        "Scheduler Algorithm",
        ["HYBRID", "ROUND_ROBIN", "RANDOM", "SHORTEST_QUEUE", "SPEA2", "MOCS"],
        index=0
    )

                       
    st.sidebar.subheader("Fog Node Configuration")
    fog_config_mode = st.sidebar.selectbox(
        "Fog Node Hardware Profile",
        list(config.FOG_CONFIG_PRESETS.keys()),
        index=0,
        help="Select a profile to auto-generate node configurations."
    )

    num_fog = st.sidebar.slider("Number of Fog Nodes to Generate", 2, 20, 10)
    
                                                           
    if 'fog_nodes_df' not in st.session_state:
                                  
        import random
        preset = config.FOG_CONFIG_PRESETS[fog_config_mode]
        initial_data = []
        for i in range(num_fog):
            initial_data.append({
                "node_id": i,
                "cpu_capacity": random.randint(preset["FOG_CPU_CAPACITY_RANGE"][0], preset["FOG_CPU_CAPACITY_RANGE"][1]),
                "cpu_speed": random.uniform(preset["FOG_CPU_SPEED_RANGE"][0], preset["FOG_CPU_SPEED_RANGE"][1]),
                "power_idle": random.uniform(preset["FOG_POWER_IDLE_RANGE"][0], preset["FOG_POWER_IDLE_RANGE"][1]),
                "power_busy": random.uniform(preset["FOG_POWER_BUSY_RANGE"][0], preset["FOG_POWER_BUSY_RANGE"][1])
            })
        st.session_state['fog_nodes_df'] = pd.DataFrame(initial_data)

    if st.sidebar.button("Regenerate Fog Nodes"):
        import random
        preset = config.FOG_CONFIG_PRESETS[fog_config_mode]
        new_data = []
        for i in range(num_fog):
            new_data.append({
                "node_id": i,
                "cpu_capacity": random.randint(preset["FOG_CPU_CAPACITY_RANGE"][0], preset["FOG_CPU_CAPACITY_RANGE"][1]),
                "cpu_speed": random.uniform(preset["FOG_CPU_SPEED_RANGE"][0], preset["FOG_CPU_SPEED_RANGE"][1]),
                "power_idle": random.uniform(preset["FOG_POWER_IDLE_RANGE"][0], preset["FOG_POWER_IDLE_RANGE"][1]),
                "power_busy": random.uniform(preset["FOG_POWER_BUSY_RANGE"][0], preset["FOG_POWER_BUSY_RANGE"][1])
            })
        st.session_state['fog_nodes_df'] = pd.DataFrame(new_data)

                                       
    with st.expander("Advanced Fog Node Configuration", expanded=True):
        st.write("Edit individual properties of Fog Nodes.")
        edited_fog_df = st.data_editor(
            st.session_state['fog_nodes_df'],
            num_rows="dynamic",
            column_config={
                "node_id": st.column_config.NumberColumn(disabled=True),
                "cpu_capacity": st.column_config.NumberColumn("Cores", min_value=1, max_value=64),
                "cpu_speed": st.column_config.NumberColumn("Speed (MIPS)", min_value=100),
                "power_idle": st.column_config.NumberColumn("Idle Power (W)"),
                "power_busy": st.column_config.NumberColumn("Busy Power (W)")
            },
            key="fog_editor"
        )

    num_iot = st.sidebar.slider("Number of IoT Devices", 5, 50, 10)
    sim_duration = st.sidebar.number_input("Simulation Duration (sec)", value=1000, step=100)

    st.sidebar.markdown("---")
    
                              
    with st.expander("Advanced IoT Device Configuration", expanded=True):
        st.write("Customize Task Type and Generation Rate for each device.")
        
                                                                 
        if 'iot_devices_df' not in st.session_state:
                                      
            iot_data = []
            for i in range(num_iot):
                iot_data.append({
                    "device_id": i,
                    "task_type": "RANDOM",
                    "arrival_rate": config.TASK_ARRIVAL_RATE
                })
            st.session_state['iot_devices_df'] = pd.DataFrame(iot_data)

        task_options = ["RANDOM"] + list(config.TASK_PROFILES.keys())
        
        edited_iot_df = st.data_editor(
            st.session_state['iot_devices_df'],
            num_rows="dynamic",
            column_config={
                "device_id": st.column_config.NumberColumn(disabled=True),
                "task_type": st.column_config.SelectboxColumn("Task Type", options=task_options, required=True),
                "arrival_rate": st.column_config.NumberColumn("Arrival Rate (tasks/s)", min_value=0.1, max_value=100.0, step=0.1)
            },
            hide_index=True,
            use_container_width=True,
            key="iot_editor_advanced"
        )

                                  
    if st.sidebar.button("Run Simulation", type="primary"):
        with st.spinner("Running Simulation... Please wait."):
                           
            config.SCHEDULER_TYPE = scheduler_type
            config.NUM_IOT_DEVICES = num_iot
            config.TASK_GENERATION_PERIOD = sim_duration
            config.FOG_CONFIG_MODE = fog_config_mode
            
                                 
                                                       
            fog_custom_list = edited_fog_df.to_dict('records')
                                 
            valid_fog_nodes = []
            for node in fog_custom_list:
                                                      
                if pd.isna(node.get('cpu_capacity')) or node.get('cpu_capacity') is None:
                    continue
                
                node['cpu_capacity'] = int(node['cpu_capacity'])
                node['node_id'] = int(node['node_id']) if pd.notna(node.get('node_id')) else 0
                valid_fog_nodes.append(node)
            
                                                               
            for idx, node in enumerate(valid_fog_nodes):
                node['node_id'] = idx
                
            config.FOG_NODES_CUSTOM_CONFIG = valid_fog_nodes
            config.NUM_FOG_NODES = len(valid_fog_nodes)

                                                       
            iot_custom_list = edited_iot_df.to_dict('records')
            valid_iot_devices = []
            for device in iot_custom_list:
                 if pd.isna(device.get('arrival_rate')) or device.get('arrival_rate') is None:
                     continue
                 device['device_id'] = int(device['device_id']) if pd.notna(device.get('device_id')) else 0
                 device['arrival_rate'] = float(device['arrival_rate'])
                 valid_iot_devices.append(device)
            
                                                                  
            for idx, device in enumerate(valid_iot_devices):
                device['device_id'] = idx
            
            config.IOT_DEVICES_CUSTOM_CONFIG = valid_iot_devices
            config.NUM_IOT_DEVICES = len(valid_iot_devices)
            
                                                                                             
            config.IOT_DEVICE_CONFIG = {} 
            
                                                              
            config.TRAINING_MODE = False
            config.BENCHMARK_MODE = False

                                 
                                                                                
            results = main.run_simulation()
            
            st.success("Simulation Complete!")
            st.session_state['has_run'] = True
            time.sleep(0.5)            
            st.rerun()

                                              
    if st.session_state.get('has_run', False):
        st.header("Simulation Results")
        
                   
        try:
            df = pd.read_csv("task_data.csv")
            
                                        
            st.markdown(f"**Configuration:** `{config.SCHEDULER_TYPE}` | Fog Nodes: `{config.NUM_FOG_NODES}` | IoT Devices: `{config.NUM_IOT_DEVICES}`")

                                  
            with st.expander("View Fog Node Configuration"):
                try:
                    df_config = pd.read_csv("fog_node_config.csv")
                    st.dataframe(df_config)
                except FileNotFoundError:
                    st.warning("Fog node configuration file not found.")

                                
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            avg_latency = df['latency'].mean()
            total_energy = df['energy_consumed'].sum()
            total_tasks = len(df)
            miss_rate = (df[df['latency'] > df['deadline']].shape[0] / total_tasks) * 100
            
            kpi1.metric("Tasks Completed", total_tasks)
            kpi2.metric("Avg Latency", f"{avg_latency:.2f} ms")
            kpi3.metric("Total Energy", f"{total_energy:.2f} J")
            kpi4.metric("Deadline Miss Rate", f"{miss_rate:.2f} %")
            
            st.divider()

                       
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Latency Distribution")
                                                     
                fig_hist = px.histogram(df, x="latency", nbins=50, title="Latency Histogram", color_discrete_sequence=['#3498db'])
                st.plotly_chart(fig_hist, use_container_width=True)
                
            with c2:
                st.subheader("Task Assignments (Fog Only)")
                                                       
                node_counts = df['node_id'].value_counts().reset_index()
                node_counts.columns = ['Node', 'Tasks']

                                      
                node_counts = node_counts[~node_counts['Node'].astype(str).str.contains("Cloud", case=False)]

                fig_pie = px.pie(node_counts, values='Tasks', names='Node', title="Tasks per Fog Node")
                st.plotly_chart(fig_pie, use_container_width=True)

            st.subheader("Timeline Analysis")
                                                                        
            fig_scatter = px.scatter(
                df, 
                x="completion_time", 
                y="latency", 
                color="task_type", 
                title="Latency vs Completion Time (congestion check)",
                opacity=0.7
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

                         
            with st.expander("View Raw Data (task_data.csv) - Fog Only"):
                                               
                df_fog = df[~df['node_id'].astype(str).str.contains("Cloud", case=False)]
                st.dataframe(df_fog)

        except FileNotFoundError:
            st.error("Result file 'task_data.csv' not found. Please run the simulation.")
    else:
        st.info("Adjust configuration in the sidebar and click **Run Simulation** to start.")

                                            
                        
                                            
with tab2:
    st.header("Benchmark Comparison")
    
    if st.button("Run Fair Benchmark", type="primary"):
        with st.status("Running Benchmark Suite...", expanded=True) as status:
            st.write("Initializing Benchmark Protocol...")
            
                                                
                                                                                      
                                                             
            config.TASK_GENERATION_PERIOD = sim_duration
            
                                            
            fog_custom_list = edited_fog_df.to_dict('records')
            valid_fog_nodes = []
            for node in fog_custom_list:
                if pd.isna(node.get('cpu_capacity')) or node.get('cpu_capacity') is None: continue
                node['cpu_capacity'] = int(node['cpu_capacity'])
                node['node_id'] = int(node['node_id']) if pd.notna(node.get('node_id')) else 0
                valid_fog_nodes.append(node)
            for idx, node in enumerate(valid_fog_nodes): node['node_id'] = idx
            
            config.FOG_NODES_CUSTOM_CONFIG = valid_fog_nodes
            config.NUM_FOG_NODES = len(valid_fog_nodes)

                                            
            iot_custom_list = edited_iot_df.to_dict('records')
            valid_iot_devices = []
            for device in iot_custom_list:
                 if pd.isna(device.get('arrival_rate')) or device.get('arrival_rate') is None: continue
                 device['device_id'] = int(device['device_id']) if pd.notna(device.get('device_id')) else 0
                 device['arrival_rate'] = float(device['arrival_rate'])
                 valid_iot_devices.append(device)
            for idx, device in enumerate(valid_iot_devices): device['device_id'] = idx
            
            config.IOT_DEVICES_CUSTOM_CONFIG = valid_iot_devices
            config.NUM_IOT_DEVICES = len(valid_iot_devices)
            config.IOT_DEVICE_CONFIG = {} 

                                                    
                                                                                                          
            try:
                run_benchmark()
                status.update(label="Benchmark Complete!", state="complete", expanded=False)
                st.session_state['benchmark_run'] = True
            except Exception as e:
                st.error(f"Benchmark Failed: {e}")
                status.update(label="Benchmark Failed", state="error")
                
    if st.session_state.get('benchmark_run', False) or os.path.exists("benchmark_results.csv"):
        st.divider()
        st.subheader("Comparative Results")
        
        try:
            bench_df = pd.read_csv("benchmark_results.csv")
            
                                       
            st.dataframe(bench_df.style.highlight_max(axis=0, subset=['TasksCompleted', 'Throughput'], color='#2ecc71')
                                     .highlight_min(axis=0, subset=['AverageLatency', 'TotalEnergy', 'DeadlineMissRate'], color='#2ecc71'))
            
            b1, b2 = st.columns(2)
            with b1:
                fig_lat = px.bar(bench_df, x="Scheduler", y="AverageLatency", title="Average Latency (Lower is Better)", color="Scheduler")
                st.plotly_chart(fig_lat, use_container_width=True)
            with b2:
                fig_eng = px.bar(bench_df, x="Scheduler", y="TotalEnergy", title="Total Energy (Lower is Better)", color="Scheduler")
                st.plotly_chart(fig_eng, use_container_width=True)
        
        except FileNotFoundError:
            st.info("No benchmark results found. Click 'Run Fair Benchmark' to start.")