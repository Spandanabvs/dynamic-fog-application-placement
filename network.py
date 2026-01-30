import random
from config import LATENCY_IOT_FOG, LATENCY_FOG_CLOUD

def get_iot_to_fog_latency():
    return random.uniform(LATENCY_IOT_FOG[0], LATENCY_IOT_FOG[1])

def get_fog_to_cloud_latency():
    return random.uniform(LATENCY_FOG_CLOUD[0], LATENCY_FOG_CLOUD[1])