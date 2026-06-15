import os
import sys
import traci

# -----------------------------
# SUMO PATH
# -----------------------------
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    raise EnvironmentError("SUMO_HOME not found")

# -----------------------------
# CURRENT FILE PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SUMO_CFG = os.path.join(BASE_DIR, "..", "simulation", "RL.sumocfg")

SUMO_CONFIG = [
    "sumo-gui",
    "-c",
    SUMO_CFG,
    "--step-length", "0.10",
    "--delay", "1000",
    "--lateral-resolution", "0"
]

sumo_started = False


# -----------------------------
# START SUMO
# -----------------------------
# def start_sumo():
#     global sumo_started

#     if not sumo_started:
#         traci.start(SUMO_CONFIG)
#         traci.gui.setSchema("View #0", "real world")
#         sumo_started = True

def start_sumo():
    # Abhi kuch mat karo
    return

# -----------------------------
# STEP
# -----------------------------
import time

def next_step():

    traci.simulationStep()

    time.sleep(0.1)


# -----------------------------
# LIVE DATA
# -----------------------------
# -----------------------------
# LIVE DATA
# -----------------------------
import time

def get_live_data():

    return {

        "EB0": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_0"),

        "EB1": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_1"),

        "EB2": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_2"),

        "SB0": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_0"),

        "SB1": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_1"),

        "SB2": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_2"),

        "phase": traci.trafficlight.getPhase("Node2")

    }

    # Simulation ko multiple steps aage badhao
    for i in range(100):
        traci.simulationStep()
        time.sleep(0.02)

    return {

        "EB0": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_0"),

        "EB1": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_1"),

        "EB2": traci.lanearea.getLastStepVehicleNumber("Node1_2_EB_2"),

        "SB0": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_0"),

        "SB1": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_1"),

        "SB2": traci.lanearea.getLastStepVehicleNumber("Node2_7_SB_2"),

        "phase": traci.trafficlight.getPhase("Node2")

    }

# -----------------------------
# CHANGE SIGNAL
# -----------------------------
def change_phase(phase):
    traci.trafficlight.setPhase("Node2", phase)


# -----------------------------
# CLOSE
# -----------------------------
def close_sumo():
    global sumo_started

    if sumo_started:
        traci.close()
        sumo_started = False