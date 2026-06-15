import random
import numpy as np

# -----------------------------
# RL Hyperparameters
# -----------------------------

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1

ACTIONS = [0, 1]

# -----------------------------
# Q Table
# -----------------------------

Q_TABLE = {}

# -----------------------------
# Stability Parameters
# -----------------------------

MIN_GREEN_STEPS = 100
last_switch_step = -MIN_GREEN_STEPS


# -----------------------------
# Initialize State
# -----------------------------

def initialize_state(state):

    if state not in Q_TABLE:
        Q_TABLE[state] = np.zeros(len(ACTIONS))


# -----------------------------
# Reward Function
# -----------------------------

def get_reward(state):

    total_queue = sum(state[:-1])

    reward = -float(total_queue)

    return reward


# -----------------------------
# Maximum Future Q Value
# -----------------------------

def get_max_q_value(state):

    initialize_state(state)

    return np.max(Q_TABLE[state])


# -----------------------------
# Action Selection
# -----------------------------

def get_action(state):

    initialize_state(state)

    if random.random() < EPSILON:

        return random.choice(ACTIONS)

    return int(np.argmax(Q_TABLE[state]))


# -----------------------------
# Update Q Table
# -----------------------------

def update_q_table(old_state, action, reward, new_state):

    initialize_state(old_state)
    initialize_state(new_state)

    old_q = Q_TABLE[old_state][action]

    future_q = get_max_q_value(new_state)

    new_q = old_q + ALPHA * (
        reward + GAMMA * future_q - old_q
    )

    Q_TABLE[old_state][action] = new_q


# -----------------------------
# Apply Decision
# -----------------------------

def decide(state):

    action = get_action(state)

    reward = get_reward(state)

    return {

        "action": action,
        "reward": reward

    }


# -----------------------------
# Return Q Table
# -----------------------------

def get_q_table():

    return Q_TABLE