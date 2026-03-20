import json
import string
import numpy as np
from config.config import PATHS



class Node:
    def __init__(self, id: str, strategy: dict, neighbors: list[str], state: str = '0', 
                 cycle: int = -1, ones_in_cycle: int = 0):
        self.id = id
        self.strategy = strategy
        self.neighbors = neighbors
        self.state = state
        self.cycle = cycle
        self.ones_in_cycle = ones_in_cycle

    def __str__(self):
        return f"id:{self.id}\nstrategy:{self.strategy}\nneighbors:{self.neighbors}\nstate:{self.state}"

class Agent:
    def __init__(self, id: str, node_data: dict, state: str = '0', random_thresh: float = 0.5):
        self.id = id
        self.weight = len(node_data)
        self.state = state
        self.is_down = False
        self.correct = False
        self.random_thresh = random_thresh
        #print(node_data)
        self.nodes = []
        for nd in node_data:
            alpha = ''.join(filter(str.isalpha,nd))
            node = Node(
                id=nd,
                strategy=node_data[nd]['strat'],
                neighbors=node_data[nd]['neigh'],
                state=state if alpha == 'a' else '0',
                cycle=node_data[nd]['cycle'],
                ones_in_cycle=node_data[nd]['ones in cycle']
            )
            self.nodes.append(node)

    def get_state(self) -> str:
        state = 0
        for node in self.nodes:
            state += int(node.state)
        self.state = str(state)
        return self.state
    
    def get_state_str(self) -> str:
        state = ''
        for node in self.nodes:
            state += node.state
        return state

    def get_ones_in_cycles(self) -> dict[int:int]:
        return {node.cycle: node.ones_in_cycle for node in self.nodes}

    def back_online(self):
        print(f"Agent {self.id} back online.")
        self.is_down = False
        self.correct = True

    def take_action(self, key: str, cycle_status: list[int], rng: np.random.Generator = None):
        for i in range(self.weight):
            if key[i] in self.nodes[i].strategy:
                self.nodes[i].state = self.nodes[i].strategy[key[i]]
            else:
                print(f"Agent {self.id}, node {self.nodes[i].id}: key '{key}' not found")
                self.nodes[i].state = rng.choice(['0', '1'])

        if self.is_down:
            print(f"Agent {self.id} (cycle {self.cycle}) is down. Randomizing state...")
            state_str = self.get_state_str()
            print(f"Should be '{state_str}' ",end=' ')
            nid = rng.choice(range(self.weight))
            for i in range(self.weight):
                if i == nid:
                    self.nodes[i].state = rng.choice(['0', '1'])
                else:
                    self.nodes[i].state = '0'
            state_str = self.get_state_str()
            print(f"but is now '{state_str}'")
        else:
            # After the node goes back online, the system should correct
            # itself.
            nid = rng.choice(range(self.weight))
            if self.nodes[nid].cycle >= 0:
                if self.correct:
                    if (cycle_status[self.nodes[nid].cycle]-self.nodes[nid].ones_in_cycle != 0):
                        performed_correction = self.correct_state(cycle_status[self.nodes[nid].cycle], nid, rng)
                    else:
                        self.correct = False  
        
            
    def correct_state(self, state_status: int, nid: int, rng: np.random.Generator = None) -> bool:
        if (state_status-self.nodes[nid].ones_in_cycle < 0) and self.get_state() == '0':
            if(rng.random() < self.random_thresh):
                prev_state = self.get_state_str()
                for i in range(self.weight):
                    if i == nid:
                        self.nodes[i].state = '1'
                    else:
                        self.nodes[i].state = '0'
                curr_state = self.get_state_str()
                print(f"Agent {self.id} correcting state from {prev_state} to {curr_state}")
                return True
            else:
                print(f"Agent {self.id} no correction performed.")
                return False
        elif (state_status-self.nodes[nid].ones_in_cycle > 0) and self.get_state() == '1':
            if(rng.random() < self.random_thresh):
                prev_state = self.get_state_str()
                for i in range(self.weight):
                    self.nodes[i].state = '0'
                curr_state = self.get_state_str()
                print(f"Agent {self.id} correcting state from {prev_state} to {curr_state}")
                return True
            else:
                print(f"Agent {self.id} no correction performed.")
                return False
        else:
            print(f"Agent {self.id} no correction performed.")
            return False


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
    total_state = ''
    for a in agent_info:
        state = 0
        for node in agent_info[a]:
            #print(agent_info[a][node])
            state = state + int(agent_info[a][node]['pattern'][t])
        total_state += str(state)
    return total_state

def get_node_state(agent_info: dict, t: int) -> dict:
    total_node_state = ''
    for a  in agent_info:
        for node in agent_info[a]:
            total_node_state += agent_info[a][node]['pattern'][t]
    return total_node_state

def get_state_from_agents(agents: list[Agent]) -> str:
    return ''.join(agent.get_state() for agent in agents)

def get_state_from_nodes(agents: list[Agent]) -> str:
    state = ''
    for agent in agents:
        for node in agent.nodes:
            state += node.state
    return state

#def print_pattern(agent_info: dict) -> None:
#    for t in range(len(agent_info['0']['pattern'])):
#        state = get_state(agent_info, t)
#        print(state)

def ones(agents: list[Agent], num_cycles: int) -> list[int]:
    ones_in_cycle = [0 for _ in range(num_cycles)]
    for agent in agents:
        for node in agent.nodes:
            #print(node.cycle, node.state)
            if node.cycle >= 0 and node.state == '1':
                ones_in_cycle[node.cycle] += 1
    return ones_in_cycle

def simulate(n: int, s: int, idx: int, Nsteps: int, 
             init_cond: str = None,
             down_times: list[int] = None, 
             down_lapses: list[int] = None,
             down_agents: list[str] = None,
             random_thresh: float = 0.5,
             seed: int = 54
             ) -> list[str]:
    #For reproducibility
    rng = np.random.default_rng(seed)

    data = load_graph_data(n, s)
    #print(data)
    agent_info = {}
    for node_id in data[idx]:
        agent_id = "".join(filter(str.isdigit,node_id))
        agent_info[agent_id] = agent_info.get(agent_id,{}) | {node_id: data[idx][node_id]}
    #print(agent_info) 
    
    node_ids = [j for i in agent_info for j in agent_info[i]]
    id_nodes = {v: k for k, v in enumerate(node_ids)}
    
    ## Initial state---
    prev_state = get_state(agent_info, 0)
    #print(prev_state)
    if init_cond:
        prev_state = init_cond
        #print(prev_state)

    ## Load agents---
    num_cycles = 0
    agents = []
    for i in agent_info:
        agent = Agent(
            id=i,
            node_data=agent_info[i],
            state=prev_state[int(i)],
            random_thresh=random_thresh
        )
        agents.append(agent)
        #print(str(agent))
        num_cycles = max(num_cycles, max(agent.get_ones_in_cycles().keys()) + 1)

    for a in agents:
        print(f"Agent {a.id} weight: {a.weight} cycles: {a.get_ones_in_cycles()}")

    prev_node_state = get_state_from_nodes(agents)
    print(get_state_from_agents(agents), get_state_from_nodes(agents))
    #print(f"num_cycles: {num_cycles}")

    ## Print info about agents that will go down---
    #for da in down_agents:
    #    print(f"da: {agents[int(da)].get_ones_in_cycles()}")

    ## Create list to store the number of ones in each cycle---
    ones_in_cycle = ones(agents, num_cycles)
    #print(ones_in_cycle)

    ## Simulation loop---
    #print(down_agents)
    pattern = [prev_node_state]
    for step in range(Nsteps):
        if down_agents is not None:
            print("Down agents:", [da for da in down_agents if agents[int(da)].is_down])
            for i in range(len(down_agents)):            
                if step == down_times[i]:
                    agents[int(down_agents[i])].is_down = True
                if step == down_times[i] + down_lapses[i]:
                    agents[int(down_agents[i])].back_online()

        for agent in agents:
            keys = []
            for node in agent.nodes:
                key = ''.join(prev_node_state[int(id_nodes[i])] for i in node.neighbors)
                keys.append(key)

            agent.take_action(keys, ones_in_cycle, rng)

        ones_in_cycle = ones(agents, num_cycles)

    #     if np.array([int(a) for a in state]).sum() == s:
    #         state_status = 'normal'
    #     elif np.array([int(a) for a in state]).sum() < s:
    #         state_status = 'low'
    #     else:
    #         state_status = 'high'
            
        state = get_state_from_agents(agents)
        pattern.append(state)
        prev_node_state = get_state_from_nodes(agents)

        print(f"step: {step}\nstate: {state} {prev_node_state}\nstate_status: {ones_in_cycle}")
        print()

    return pattern
