from __future__ import annotations

import numpy as np
import json
from pathlib import Path
from typing import Dict, List

from config.config import PATHS


class EquitableAgent:
    """Represents an agent in the equitable graph with pattern and strategy information."""
    
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.pattern: List[str] = []
        self.neigh: List[str] = []
        self.strat: Dict[str, str] = {"0": "0", "1": "1"}
        self.input_freq: Dict[str, int] = {}
        self.cycle: int = -1
        self.ones_in_cycle: int = 0

    def __str__(self) -> str:
        return (f"Agent: {self.id}\n pattern: {self.pattern}\n neighbors {self.neigh}\n "
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


class GraphCreator:
    """Creates and manages equitable graphs with specified parameters."""
    
    def __init__(self, N: int, s: int) -> None:
        """
        Initialize graph creator with parameters.
        
        Args:
            N: Number of agents
            s: Step parameter for graph structure
        """
        self.N = N
        self.s = s
        self.agents: List[EquitableAgent] = []
        self.gcd = np.gcd(N, s)
        self.n = N // self.gcd  # cycle length
        self.b = s // self.gcd  # ones in cycle
        self.twin_g_size = self.gcd
        self.twin_groups: List[List[EquitableAgent]] = []
        
        # Initialize project root path
        self.project_root = Path(__file__).parent.parent.parent
        
    def create_agents(self) -> None:
        """Create all agents for the graph."""
        self.agents = [EquitableAgent(id=i) for i in range(self.N)]
        self.twin_groups = [self.agents[i:i+self.twin_g_size] 
                           for i in range(0, self.N, self.twin_g_size)]
    
    def set_neighbors(self) -> None:
        """Set neighbor relationships for all agents."""
        # Create the main cycle
        for g_id in range(self.n):
            next_id = (g_id + 1) % self.n
            self.agents[self.twin_groups[g_id][0].id].cycle = 0
            self.agents[self.twin_groups[next_id][0].id].neigh.append(
                str(self.twin_groups[g_id][0].id))

        # Add the rest of the neighbors
        for g_id in range(self.n):
            next_id = (g_id + 1) % self.n
            for i in range(1, self.twin_g_size):
                self.agents[self.twin_groups[next_id][i].id].neigh.append(
                    str(self.twin_groups[g_id][0].id))
    
    def set_number_of_ones_in_cycle(self) -> None:
        """Set the number of ones in cycle for agents in the main cycle."""
        for g_id in range(self.n):
            self.agents[self.twin_groups[g_id][0].id].ones_in_cycle = int(self.b)
    
    def generate_patterns(self) -> None:
        """Generate patterns for all agents based on graph structure."""
        # Initial state in cycle
        ones = self.b
        for i in range(self.N):
            if self.agents[i].cycle == 0:
                if ones > 0:
                    self.agents[i].pattern.append('1')
                    ones -= 1
                else:
                    self.agents[i].pattern.append('0')

        # Initial state off cycle (copy action of twin in cycle)
        for g_id in range(self.n):
            for i in range(1, self.twin_g_size):
                self.agents[self.twin_groups[g_id][i].id].pattern.append(
                    self.agents[self.twin_groups[g_id][0].id].pattern[0])
        
        # Simulate the rest of the period
        for t in range(1, self.n):
            for a in self.agents:
                a.pattern.append(self.agents[int(a.neigh[0])].pattern[t-1])
        
        # Input frequency
        freq_1 = int(sum(map(int, self.agents[0].pattern)))
        freq_0 = int(self.n - freq_1)
        for a in self.agents:
            a.input_freq = {"0": freq_0, "1": freq_1}
    
    def build_graph(self) -> None:
        """Build the complete graph by executing all setup steps."""
        self.create_agents()
        self.set_neighbors()
        self.set_number_of_ones_in_cycle()
        self.generate_patterns()
    
    def to_structure(self) -> List[Dict[int, Dict[str, object]]]:
        """
        Convert graph data to structured format for serialization.
        
        Returns:
            List containing a dictionary mapping agent IDs to their data.
        """
        struct: List[Dict[int, Dict[str, object]]] = [{}]
        for a in self.agents:
            struct[0][a.id] = a.to_dict()
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
        if output_path is None:
            output_path = (self.project_root / "data" / "graphs" / 
                          f"graph_data_N{self.N:d}s{self.s:d}.json")
        
        struct = self.to_structure()
        with open(output_path, 'w') as json_file:
            json.dump(struct, json_file)
        
        return output_path
    
    def print_agents(self) -> None:
        """Print information about all agents."""
        for a in self.agents:
            print(a)


