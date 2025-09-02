
import json
import numpy as np
from config.config import PATHS


class Agent:
    def __init__(self, id: int, strategy: dict, neighbors: list[int], state: str = '0'):
        self.id = id
        self.strategy = strategy
        self.neighbors = neighbors
        self.state = state
        self.is_down = False

    def take_action(self, key):
        if key in self.strategy:
            self.state = self.strategy[key]
        else:
            print(f"Agent {self.id}: key '{key}' not found")
            self.state = np.random.choice(['0', '1'])

        if self.is_down:
            print(f"Agent {self.id} is down. Randomizing state...\nShould be '{self.state}' ",end=' ')
            self.state = np.random.choice(['0', '1'])
            print(f"but is now '{self.state}'")

    def correct(self, state_status: str):
        if state_status == 'low' and self.state == '0':
            self.state = '1'
            print(f"Agent {self.id} correcting state to '1'")
            return True
        elif state_status == 'high' and self.state == '1':
            self.state = '0'
            print(f"Agent {self.id} correcting state to '0'")
            return True
        else:
            print(f"Agent {self.id} no correction performed.")
            return False

    def __str__(self):
        return f"id:{self.id}\nstrategy:{self.strategy}\nneighbors:{self.neighbors}\nstate:{self.state}"


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

def get_state_from_agents(agents: list[Agent]) -> str:
    return ''.join(agent.state for agent in agents)

def print_pattern(agent_info: dict) -> None:
    for t in range(len(agent_info['0']['pattern'])):
        state = get_state(agent_info, t)
        print(state)

def simulate(n: int, s: int, idx: int, Nsteps: int, 
             init_cond: str = None,
             down_time: int = 0, 
             down_lapse: int = 0, down_agent: int = None) -> list[str]:
    data = load_graph_data(n, s)
    #print(data)
    agent_info = data[idx]
    #print_pattern(agent_info)
    
    prev_state = get_state(agent_info, 0)
    if init_cond:
        prev_state = init_cond
    #print(prev_state)

    agents = []
    for i in range(len(agent_info)):
        agent = Agent(
            id=i,
            strategy=agent_info[str(i)]['strat'],
            neighbors=agent_info[str(i)]['neigh'],
            state=prev_state[i]
        )
        agents.append(agent)
        #print(str(agent))
    print(get_state_from_agents(agents))


    
    pattern = [prev_state]
    # is_down = False
    state_status = 'normal'
    countdown = False
    apply_correction = False
    wait_steps = n
    for step in range(Nsteps):
        if down_agent is not None:
            if step >= down_time and not agents[down_agent].is_down:
                agents[down_agent].is_down = True
            if agents[down_agent].is_down and step >= down_time + down_lapse:
                agents[down_agent].is_down = False

        state = ''
        for agent in agents:
            key = ''.join(prev_state[int(i)] for i in agent.neighbors)
            #print(key)

            agent.take_action(key)

            if apply_correction and agent.id == down_agent:
                print("Correcting...")
                performed_correction = agent.correct(state_status)
                if performed_correction:
                    apply_correction = False
                    wait_steps = n

            state += agent.state

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
        if (state_status != 'normal') and (not agents[down_agent].is_down):
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

        print(f"state: {state}\nstate_status: {state_status}\nagent.is_down: {agents[down_agent].is_down}\nwait_steps: {wait_steps}\napply_correction: {apply_correction}\n")

    return pattern
