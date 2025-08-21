
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
            state += action

        pattern.append(state)
        prev_state = state

    return pattern
