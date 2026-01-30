# Application Placement Technique for Improved Latency and Energy Optimization in Dynamic Fog Environment

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Simulation](https://img.shields.io/badge/Simulation-SimPy-orange.svg)](https://simpy.readthedocs.io/)
[![UI](https://img.shields.io/badge/UI-Streamlit-ff4b4b.svg)](ui_simple.py)

---

## 📌 Project Overview

Fog computing has emerged as a promising paradigm to support latency-sensitive and energy-constrained Internet of Things (IoT) applications by enabling computation closer to end users. However, fog environments are characterized by limited computational capacity, heterogeneous resources, dynamic workloads, bandwidth constraints, and increased energy consumption.

This project presents a **simulation-based application placement and task scheduling framework** for a dynamic **IoT–Fog–Cloud environment**, aimed at minimizing **task latency** and optimizing **energy consumption**. A **Hybrid Reinforcement Learning and Firefly Optimization–based scheduling approach** is proposed and evaluated against conventional scheduling techniques.

---

## 📝 Abstract

With the rapid growth of IoT devices, massive volumes of data are generated and require timely processing. Traditional cloud-centric computing often suffers from high latency and bandwidth limitations, making it unsuitable for real-time and delay-sensitive applications. Fog computing addresses these challenges by decentralizing computation and bringing resources closer to data sources.

Despite its advantages, fog computing introduces new challenges such as limited resource capacity, dynamic workloads, and energy constraints. Static and rule-based scheduling algorithms fail to adapt effectively to these changing conditions. This project develops a simulation-based environment that enables intelligent and adaptive task scheduling using a hybrid learning and optimization approach.

The proposed system evaluates latency and energy consumption metrics to make improved scheduling decisions dynamically. Simulation results demonstrate that the proposed scheduling strategy improves response time, reduces energy usage, and enhances overall system performance when compared to conventional scheduling approaches.

---

## 🎯 Objectives of the Project

The specific objectives of this project are:

1. To design and implement a simulation environment modeling IoT devices, fog nodes, and cloud resources.
2. To develop an efficient application placement strategy for fog and cloud environments.
3. To minimize end-to-end task latency for delay-sensitive applications.
4. To reduce energy consumption of fog and cloud resources.
5. To improve resource utilization and prevent node overloading.
6. To perform a fair comparative analysis of different scheduling strategies.

---

## ⭐ Why This Project Is Useful

- Addresses latency and energy challenges in large-scale IoT systems  
- Demonstrates adaptive scheduling in dynamic fog environments  
- Enables fair and reproducible benchmarking of scheduling algorithms  
- Suitable for academic research, final-year projects, and performance evaluation  
- Provides an extensible framework for experimenting with intelligent schedulers  

---

## 🧠 Proposed Scheduling Methodology

### Hybrid Reinforcement Learning + Firefly Optimization

- **Q-Learning Agent**
  - Learns optimal trade-offs between latency and energy consumption
  - Adapts scheduling policies based on system state (queue length, deadline miss rate)
  - Continuously improves decisions through online learning

- **Firefly Optimization Algorithm**
  - Performs node-level optimization
  - Selects the most suitable fog or cloud node based on estimated cost

This hybrid approach combines the adaptability of reinforcement learning with the efficiency of swarm-based optimization.

---

## 🏗️ System Architecture

**System Components:**

- **IoT Devices**  
  Generate heterogeneous tasks with varying CPU, data size, and deadline requirements.

- **Fog Nodes**  
  Resource-constrained, heterogeneous nodes with energy-aware execution.

- **Cloud Node**  
  High-capacity centralized resource for offloading tasks.

- **Scheduler**  
  Implements multiple scheduling strategies:
  - HYBRID (Proposed)
  - SPEA2
  - MOCS
  - Round Robin
  - Shortest Queue
  - Random

- **Results Collector**  
  Logs task-level and system-level performance metrics.

---

## ⚙️ Hardware and Software Requirements

### Hardware Requirements
- Standard PC or Laptop
- Minimum 8 GB RAM recommended

### Software Requirements
- Python 3.9+
- SimPy
- NumPy
- Pandas
- Streamlit
- Matplotlib / Plotly

---

## 🚀 Getting Started

### Installation

```bash
git clone <repository-url>
cd fog-cloud-scheduler
pip install -r requirements.txt
