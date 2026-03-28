from __future__ import annotations

import numpy as np
import json
import string
import re
from pathlib import Path
from typing import Dict, List

from config.config import PATHS


class FairNode:
    """Represents a node in the fair graph with pattern and strategy information."""
    
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.pattern: List[str] = []
        self.neigh: List[str] = []
        self.strat: Dict[str, str] = {"0": "0", "1": "1"}
        self.input_freq: Dict[str, int] = {}
        self.cycle: int = -1
        self.ones_in_cycle: int = 0

    def __str__(self) -> str:
        return (f"Node: {self.id}\n pattern: {self.pattern}\n neighbors {self.neigh}\n "
                f"strategy: {self.strat}\n input_freq: {self.input_freq}\n "
                f"cycle: {self.cycle}\n ones_in_cycle: {self.ones_in_cycle}")

    def to_dict(self) -> Dict[str, object]:
        """Convert agent data to dictionary format for JSON serialization."""
        return {
            "pattern": self.pattern,
            "neigh": self.neigh,
            "strat": self.strat,
            "input freq": self.input_freq,
            "cycle": self.cycle,
            "ones in cycle": self.ones_in_cycle
        }


class FairWeightedAgent:
    def __init__(self, 
                 id: str,
                 weight: int
                 ) -> None:
        self.id: str = id
        self.weight: int = weight
        self.nodes: List[FairNode] = [FairNode(id=str(id)+str(string.ascii_lowercase[i])) for i in range(weight)]

    def __str__(self) -> str:
        return f"Agent: {self.id}\n weight: {self.weight}\n nodes: {[node.id for node in self.nodes]}"
    

class WeightedGraphCreator:
    """Creates and manages fair weighted graphs with specified parameters."""

    def __init__(self, agents_info: Dict[str, int], s: int) -> None:
        """
        Initialize graph creator with parameters.
        
        Args:
            agents: Dictionary of agents with their weights
            s: Step parameter for graph structure
        """
        self.agents = {str(i): FairWeightedAgent(str(i),w) for i, w in agents_info.items()}
        self.s = s
        self.graph: List[str] = ['x' for _ in range(self.s)]
        for a in agents_info:
            ar = self.process(str(a), agents_info[a], self.s)
            self.insert_process(ar)
        
        # Initialize project root path
        self.project_root = Path(__file__).parent.parent.parent

    def build_graph(self) -> None:
        # Add extra nodes in the graph to the agents 
        for id in self.graph:
            if id[-1] == 'r':
                num = ''.join(re.findall(r'[0-9]+', id))
                if num:
                    node = FairNode(id)
                    self.agents[num].nodes.append(node) 
        #print(self.graph)
        for agent in self.agents.values():
            for node in agent.nodes:
                idx = self.graph.index(node.id)
                idx_neigh = (idx - 1) % len(self.graph)
                node.neigh.append(self.graph[idx_neigh])
                node.pattern = ['1' if i == idx else '0' for i in range(len(self.graph))]
                node.input_freq = {'0': len(self.graph)-1, '1': 1}
                node.cycle = 0
                node.ones_in_cycle = self.s
                #print(node)

    def process(self, id: str, weight: int, b: int) -> List[str]:
        proc_string = ''
        for i in range(weight):
            proc_string += str(id)+string.ascii_lowercase[i]+','
            for j in range(1, b):
                proc_string += 'x'+','
        return proc_string.split(',')[:-1]
    
    def repeated_to_ghost(self):
        for i in range(len(self.graph)):
            if self.graph[i][-1] == 'r':
                self.graph[i] = 'x'
    
    def shift_processes_left(self):
        for k in range(self.s): #shift all stacks
            pos_1st_ghost = -1 
            try:
                pos_1st_ghost = [self.graph[i] for i in range(k,len(self.graph),self.s)].index('x')*self.s+k
            except ValueError:
                pos_1st_ghost = len(self.graph)
            if pos_1st_ghost < len(self.graph):
                for i in range(pos_1st_ghost, len(self.graph)-(self.s-k), self.s):
                    self.graph[i] = self.graph[i+self.s] 
                if pos_1st_ghost < len(self.graph)-(self.s-k):
                    self.graph[len(self.graph)-(self.s-k)] = 'x'

    def merge(self, p, pos_ini=None):
        pos_1st_ghost = -1
        if pos_ini:
            pos_1st_ghost = pos_ini
        else:
            try:
                pos_1st_ghost = self.graph.index('x')
            except ValueError:
                pos_1st_ghost = len(self.graph)
        if pos_1st_ghost == len(self.graph):
            self.graph += p
            return
        j = 0
        for i in range(pos_1st_ghost, len(self.graph)):
            j = i - pos_1st_ghost
            if j >= len(p):
                break
            if self.graph[i] == 'x' and p[j] != 'x':
                self.graph[i] = p[j]
        for k in range(j+1,len(p)):
            self.graph.append(p[k])
    
    def delete(self, p):
        pid = ''.join(re.findall(r'[0-9]+', p[0]))
        first_pos = -1
        for i in range(len(self.graph)):
            num = ''.join(re.findall(r'[0-9]+', self.graph[i]))
            if num == pid:
                first_pos = i
                break
        if first_pos == -1:
            print(f"Process with id {pid} not found")
        else:
            for i in range(first_pos, first_pos+len(p), self.s):
                self.graph[i] = 'x'

    def balance_graph(self):
        #Get the processor with the shortest load
        shortest_stack_idx = -1
        shortest_stack_len = float('inf')
        stack_lengths = []
        for idx in range(self.s):
            stack_len = len([self.graph[i] for i in range(idx, len(self.graph), self.s) if self.graph[i] != 'x'])
            stack_lengths.append(stack_len)
            if stack_len < shortest_stack_len:
                shortest_stack_len = stack_len
                shortest_stack_idx = idx
        if sum(stack_lengths) == 0:
            return

        #Get the processor with most processes
        max_elems_idx = -1
        max_elems = -1
        min_weight_id = None
        for idx in range(self.s):
            pids = [''.join(re.findall(r'[0-9]+', self.graph[i])) for i in range(idx, len(self.graph), self.s) if self.graph[i] != 'x']
            w = [pids.count(i) for i in set(pids)]
            elems = len(set(pids))
            if elems > max_elems:
                max_elems = elems
                max_elems_idx = idx
                min_weight = 0
                if len(w) > 0:
                    min_weight = min(w)
                    min_weight_id = pids[w.index(min_weight)]
        #print('shortest stack idx: ', shortest_stack_idx, ' with length: ', shortest_stack_len)
        #print('max elems idx: ', max_elems_idx, ' with length: ', stack_lengths[max_elems_idx])

        #Move minimum weight process from the processor with most processes to the one with the shortest load
        if max_elems > 1 and shortest_stack_len < stack_lengths[max_elems_idx]:
            p = self.process(min_weight_id, min_weight)
            self.delete(p)
            self.shift_processes_left()
            ini = [self.graph[i] for i in range(shortest_stack_idx, len(self.graph), self.s)].index('x') * self.s + shortest_stack_idx
            self.merge(p, pos_ini=ini)
    
    def fit_ghosts(self):
        while self.graph[-1] == 'x':
            if len(self.graph) == self.s:
                break
            self.graph.pop()
        while len(self.graph) % self.s != 0:
            self.graph.append('x')

    def check_change(self, i, j):
        if self.graph[j] != 'x':
            num = ''.join(re.findall(r'[0-9]+', self.graph[j]))
            letters = ''.join(re.findall(r'[a-z]+', self.graph[j]))
            if letters[-1] == 'r':
                letters = letters[:-1]
            let_num = string.ascii_lowercase.index(letters[-1])
            self.graph[i] = num+string.ascii_lowercase[let_num+1]+'r'
            
    def fill_extra_nodes(self):
        for i in range(len(self.graph)):
            if i%2 == 0:
                if self.graph[i] == 'x':
                    #check left
                    j = (i-self.s) % len(self.graph)
                    self.check_change(i,j)
                if self.graph[i] == 'x':
                    #check right
                    j = (i+self.s) % len(self.graph)
                    self.check_change(i,j)
            else:
                if self.graph[i] == 'x':
                    #check right
                    j = (i+self.s) % len(self.graph)
                    self.check_change(i,j)
                if self.graph[i] == 'x':
                    #check left
                    j = (i-self.s) % len(self.graph)
                    self.check_change(i,j)

    def insert_process(self, p):
        # Remove the 'r' tags from the process to be inserted and replace them with 'x'
        self.repeated_to_ghost()

        # Shift processes left to fill the first ghost nodesa = node
        self.shift_processes_left()

        # Insert the new process in the remaining ghost nodes
        self.merge(p)

        # Adjust the length of the graph with ghost nodes if necessary
        self.fit_ghosts()

        # Replace ghost nodes with repeated tags where possible
        self.fill_extra_nodes()
    
    def delete_process(self, p):
        # Remove the 'r' tags from the process to be inserted and replace them with 'x'
        self.repeated_to_ghost()

        # Replace the process to be deleted with ghost nodes
        self.delete(p)

        # Balance the graph after deletion by moving processes from right to left to fill the ghost nodes
        self.balance_graph()

        # Shift processes left to fill the first ghost nodes
        self.shift_processes_left()

        # Adjust the length of the graph with ghost nodes if necessary
        self.fit_ghosts()

        # Replace ghost nodes with repeated tags where possible
        self.fill_extra_nodes()
    
    def to_structure(self) -> List[Dict[int, Dict[str, object]]]:
        """
        Convert graph data to structured format for serialization.
        
        Returns:
            List containing a dictionary mapping agent IDs to their data.
        """
        struct: List[Dict[int, Dict[str, object]]] = [{}]
        for agent in self.agents:
            for node in self.agents[agent].nodes:
                struct[0][node.id] = node.to_dict()
        return struct

    def save_to_json(self, output_path: Path = None) -> Path:
        """
        Save graph data to JSON file.
        
        Args:
            output_path: Optional custom path for output file. 
                        If None, uses default path in data/graphs.
        
        Returns:
            Path to the saved JSON file.
        """
        N = len(self.graph)
        if output_path is None:
            output_path = (self.project_root / "data" / "graphs" / 
                          f"graph_data_N{N:d}s{self.s:d}.json")
        
        struct = self.to_structure()
        with open(output_path, 'w') as json_file:
            json.dump(struct, json_file)
        
        return output_path