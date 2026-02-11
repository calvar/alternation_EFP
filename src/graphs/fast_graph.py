import numpy as np
import json

from typing import Dict, List
#from config.config import PATHS

from pathlib import Path
project_root = Path(__file__).parent.parent.parent

class EquitableAgent:
    def __init__(self, 
                 id: int
                 ) -> None:
        self.id: int = id
        self.pattern: List[str] = []
        self.neigh: List[str] = []
        self.strat: Dict[str, str] = {"0": "0", "1": "1"}
        self.input_freq: Dict[str, int] = {}
        self.cycle: int = -1
        self.ones_in_cycle: int = 0

    def __str__(self) -> str:
        return f"Agent: {self.id}\n pattern: {self.pattern}\n neighbors {self.neigh}\n strategy: {self.strat}\n input_freq: {self.input_freq}\n cycle: {self.cycle}\n ones_in_cycle: {self.ones_in_cycle}"

    
def set_neighbors(agents: List[EquitableAgent], N: int, s: int) -> None:
    gcd = np.gcd(N, s)
    n = N // gcd

    twin_g_size = gcd
    twin_groups = [agents[i:i+twin_g_size] for i in range(0, N, twin_g_size)]
    #print(f"twin groups: {[ [agent.id for agent in group] for group in twin_groups ]}")

    # Create the main cycle
    for g_id in range(n):
        next_id = (g_id+1) % n
        agents[twin_groups[g_id][0].id].cycle = 0
        agents[twin_groups[next_id][0].id].neigh.append(str(twin_groups[g_id][0].id))

    # Add the rest of the neighbors
    for g_id in range(n):
        next_id = (g_id+1) % n
        for i in range(1,twin_g_size):
            agents[twin_groups[next_id][i].id].neigh.append(str(twin_groups[g_id][0].id))

def set_number_of_ones_in_cycle(agents: List[EquitableAgent], N: int, s: int) -> None:
    gcd = np.gcd(N, s)
    n = N // gcd
    b = s // gcd

    twin_g_size = gcd
    twin_groups = [agents[i:i+twin_g_size] for i in range(0, N, twin_g_size)]

    for g_id in range(n):
        agents[twin_groups[g_id][0].id].ones_in_cycle = int(b)

def generate_patterns(agents: List[EquitableAgent], N: int, s: int) -> None:
    gcd = np.gcd(N, s)
    n = N // gcd
    b = s // gcd

    twin_g_size = gcd
    twin_groups = [agents[i:i+twin_g_size] for i in range(0, N, twin_g_size)]

    # Initial state in cycle
    ones = b
    for i in range(N):
        if agents[i].cycle == 0:
            if ones > 0:
                agents[i].pattern.append('1')
                ones -= 1
            else:
                agents[i].pattern.append('0')

    # Initial state off cycle (copy action of twin in cycle)
    for g_id in range(n):
        for i in range(1,twin_g_size):
            agents[twin_groups[g_id][i].id].pattern.append(agents[twin_groups[g_id][0].id].pattern[0])
    
    # Simulate the rest of the period
    for t in range(1,n):
        for a in agents:
            a.pattern.append(agents[int(a.neigh[0])].pattern[t-1])
        
    # Input frequency
    freq_1 = int(sum(map(int, agents[0].pattern)))
    freq_0 = int(n - freq_1)
    for a in agents:
        a.input_freq = {"0": freq_0, "1": freq_1}




if __name__ == "__main__":
    N = 15
    s = 9


    agents = [EquitableAgent(id=i) for i in range(N)]
    
    set_neighbors(agents, N, s)
    set_number_of_ones_in_cycle(agents, N, s)
    generate_patterns(agents, N, s)
    #for a in agents:        
    #    print(a)

    struct: List[Dict[int, Dict[str, object]]] = [{}]
    for a in agents:
        struct[0][a.id] = {"pattern": a.pattern, 
                           "neigh": a.neigh, 
                           "strat": a.strat,
                           "input freq": a.input_freq, 
                           "cycle": a.cycle, 
                           "ones in cycle": a.ones_in_cycle}
        
    print(struct)
    
    # #graph_path = PATHS['graphs'] / f"graph_data_N{N:d}s{s:d}.json"
    # graph_path = project_root / "data" / "graphs" / f"graph_data_N{N:d}s{s:d}.json"
    # with open(graph_path, 'w') as json_file:
    #     json.dump(struct, json_file)
        
