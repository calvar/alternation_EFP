import json
import numpy as np
from config.config import PATHS



class Agent:
    def __init__(self, id: int, strategy: dict, neighbors: list[int], state: str = '0', 
                 cycle: int = -1, ones_in_cycle: int = 0):
        self.id = id
        self.strategy = strategy
        self.neighbors = neighbors
        self.state = state
        self.cycle = cycle
        self.ones_in_cycle = ones_in_cycle
        self.is_down = False
        self.correct = False

    def back_online(self):
        print(f"Agent {self.id} back online.")
        self.is_down = False
        self.correct = True

    def take_action(self, key: str, cycle_status: list[int], rng: np.random.Generator = None):
        if key in self.strategy:
            self.state = self.strategy[key]
        else:
            print(f"Agent {self.id}: key '{key}' not found")
            self.state = rng.choice(['0', '1'])

        if self.is_down:
            print(f"Agent {self.id} (cycle {self.cycle}) is down. Randomizing state...\nShould be '{self.state}' ",end=' ')
            self.state = rng.choice(['0', '1'])
            print(f"but is now '{self.state}'")
        else:
            # After the node goes back online, the system should correct
            # itself.
            if self.cycle >= 0:
                if self.correct:
                    if (cycle_status[self.cycle]-self.ones_in_cycle != 0):
                        performed_correction = self.correct_state(cycle_status[self.cycle])
                    else:
                        self.correct = False  
        
            
    def correct_state(self, state_status: int):
        if (state_status-self.ones_in_cycle < 0) and self.state == '0':
            self.state = '1'
            print(f"Agent {self.id} correcting state from '0' to '1'")
            return True
        elif (state_status-self.ones_in_cycle > 0) and self.state == '1':
            self.state = '0'
            print(f"Agent {self.id} correcting state from '1' to '0'")
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

def ones(agents: list[Agent], num_cycles: int) -> list[int]:
    ones_in_cycle = [0 for _ in range(num_cycles)]
    for agent in agents:
        if agent.cycle >= 0 and agent.state == '1':
            ones_in_cycle[agent.cycle] += 1
    return ones_in_cycle

def simulate(n: int, s: int, idx: int, Nsteps: int, 
             init_cond: str = None,
             down_times: list[int] = None, 
             down_lapses: list[int] = None, 
             down_agents: list[int] = None,
             seed: int = 54) -> list[str]:
    #For reproducibility
    rng = np.random.default_rng(seed)

    data = load_graph_data(n, s)
    #print(data)
    agent_info = data[idx]
    #print_pattern(agent_info)
    
    prev_state = get_state(agent_info, 0)
    if init_cond:
        prev_state = init_cond
    #print(prev_state)

    num_cycles = 0
    agents = []
    for i in range(len(agent_info)):
        agent = Agent(
            id=i,
            strategy=agent_info[str(i)]['strat'],
            neighbors=agent_info[str(i)]['neigh'],
            state=prev_state[i],
            cycle=agent_info[str(i)]['cycle'],
            ones_in_cycle=agent_info[str(i)]['ones in cycle']
        )
        agents.append(agent)
        #print(str(agent))
        num_cycles = max(num_cycles, agent.cycle + 1)
    #print(get_state_from_agents(agents))
    print(f"num_cycles: {num_cycles}")

    for da in down_agents:
        print(f"da: {agents[da].cycle}")


    ones_in_cycle = ones(agents, num_cycles)
    pattern = [prev_state]
    for step in range(Nsteps):
        if down_agents is not None:
            for i in range(len(down_agents)):            
                if step == down_times[i]:
                    agents[down_agents[i]].is_down = True
                if step == down_times[i] + down_lapses[i]:
                    agents[down_agents[i]].back_online()

        state = ''
        for agent in agents:
            key = ''.join(prev_state[int(i)] for i in agent.neighbors)
            #print(key)

            agent.take_action(key, ones_in_cycle, rng)

            state += agent.state

        ones_in_cycle = ones(agents, num_cycles)

    #     if np.array([int(a) for a in state]).sum() == s:
    #         state_status = 'normal'
    #     elif np.array([int(a) for a in state]).sum() < s:
    #         state_status = 'low'
    #     else:
    #         state_status = 'high'
            
        pattern.append(state)
        prev_state = state

        print(f"state: {state}\nstate_status: {ones_in_cycle}")
        print()

    return pattern
