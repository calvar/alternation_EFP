
import json
import numpy as np
from config.config import PATHS


def load_graph_data(n: int, s: int) -> dict:
    """
    Load graph data from a JSON file.
    
    Args:
        n: The first parameter for the filename
        s: The second parameter for the filename
        
    Returns:
        Dictionary containing the graph data
    """

    filename = f'graph_data_N{n:d}s{s:d}.json'

    file_path = PATHS['graphs'] / filename
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def get_state(agent_info: dict, t: int) -> str:
    ini_st = ''.join(agent_info[i]['pattern'][t] for i in agent_info)
    return ini_st

def print_pattern(agent_info: dict) -> None:
    for t in range(len(agent_info['0']['pattern'])):
        state = get_state(agent_info, t)
        print(state)

def simulate(n: int, s: int, idx: int, Nsteps: int, 
             init_cond: str = None,
             down_time: int = 0, 
             down_lapse: int = 0, down_agent: int = None) -> list[str]:
    data = load_graph_data(n, s)
    agent_info = data[idx]
    #print_pattern(agent_info)

    prev_state = get_state(agent_info, 0)
    if init_cond:
        prev_state = init_cond

    pattern = [prev_state]
    is_down = False
    state_status = 'normal'
    countdown = False
    apply_correction = False
    wait_steps = n
    for step in range(Nsteps):
        if down_agent is not None:
            if step >= down_time and not is_down:
                is_down = True
            if is_down and step >= down_time + down_lapse:
                is_down = False

        state = ''
        for agent in agent_info:
            key = ''.join(prev_state[int(i)] for i in agent_info[agent]['neigh'])
            
            action = ''
            if key in agent_info[agent]['strat']:
                action = agent_info[agent]['strat'][key]
            else:
                action = np.random.choice(['0', '1'])

            if is_down and int(agent) == down_agent:
                action = np.random.choice(['0', '1'])

            if apply_correction and int(agent) == down_agent:
                if state_status == 'low' and action == '0':
                    action = '1'
                elif state_status == 'high' and action == '1':
                    action = '0'
                apply_correction = False

            state += action

        if np.array([int(a) for a in state]).sum() == s:
            state_status = 'normal'
        elif np.array([int(a) for a in state]).sum() < s:
            state_status = 'low'
        else:
            state_status = 'high'

        # After the node goes back online, allow for n steps to 
        # pass before applying a correction. If the down node is
        # not in a cycle, the system should correct itself after, at most,
        # n steps.
        if (state_status != 'normal') and (not is_down):
            if wait_steps == n:
                countdown = True
            if countdown:
                wait_steps -= 1
            if countdown and wait_steps == 0:
                countdown = False
                wait_steps = n
                apply_correction = True
            
        pattern.append(state)
        prev_state = state

        print(state, state_status, is_down, wait_steps, apply_correction)

    return pattern
