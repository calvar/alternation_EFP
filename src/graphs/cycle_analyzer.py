import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any

from config.config import PATHS

class CycleAnalyzer:
    """
    A class to analyze cycles in graph data and augment JSON files with cycle information.
    
    This class:
    - Loads graph data from JSON files
    - Detects simple cycles using NetworkX
    - Adds 'cycle' and 'ones in cycle' attributes to each node
    - Saves the modified data back to the JSON file
    """

    def __init__(self, num_nodes: int, num_steps: int) -> None:
        """
        Initialize the CycleAnalyzer with a graph data file.
        
        Args:
            num_nodes: Number of nodes (agents) in the graph
            num_steps: Number of available spots in the system
        """
        self.N = num_nodes
        self.s = num_steps

        self.graph_file_path = PATHS['graphs'] / f"graph_data_N{self.N:d}s{self.s:d}.json"
        self.struct = None
        self.cycles = []  # Placeholder for cycles list

    def load_graph_data(self) -> None:
        """Load the graph data from the JSON file."""
        with open(self.graph_file_path, 'r') as f:
            self.struct = json.load(f)

    def detect_cycles(self, Npat: int = 0) -> List[List[str]]:
        """
        Detect simple cycles in the graph using NetworkX.
        
        Args:
            Npat: The pattern index to analyze (default: 0)
            
        Returns:
            List of cycles, where each cycle is a list of node IDs (as strings)
        """
        
        # Build directed graph from the struct
        DG = nx.DiGraph()
        DG.add_nodes_from([str(i) for i in range(self.N)])
        
        # Add edges for nodes with strategies
        for n1 in self.struct[Npat]:
            for n2 in self.struct[Npat][str(n1)].get("neigh", []):
                if len(self.struct[Npat][str(n1)].get("strat", {})) > 1:
                    DG.add_edge(n2, n1)
        
        # Detect simple cycles
        cycles = list(nx.simple_cycles(DG))
        return cycles

    def print_cycles(self, Npat: int = 0) -> None:
        """Print information about detected cycles."""
        if self.cycles[Npat] is None:
            print("No cycles detected. Call detect_cycles() first.")
            return
            
        print(f"Number of simple cycles: {len(self.cycles[Npat])}")
        for cycle in self.cycles[Npat]:
            print(" -> ".join(cycle))

    def print_cycle_ones(self, Npat: int = 0) -> None:
        """
        Print the number of 1s in each cycle.
        
        Args:
            Npat: The pattern index to analyze (default: 0)
        """
            
        for c in range(len(self.cycles[Npat])):
            cycle = self.cycles[Npat][c]
            ones_count = 0
            for i in cycle:
                ones_count += int(self.struct[Npat][i]["pattern"][0])
            print(f"Cycle {c}: {ones_count} ones, Pattern: {' -> '.join(cycle)}")

    def augment_struct_with_cycles(self) -> None:
        """
        Add 'cycle' and 'ones in cycle' keys to all nodes in the struct.
        """        
        if self.struct is None:
            raise ValueError("No graph data loaded. Call load_graph_data() first.")
        
        # Augment each pattern
        for pattern_idx in range(len(self.struct)):
            self.cycles.append(self.detect_cycles(Npat=pattern_idx))
            for i in range(self.N):
                self.struct[pattern_idx][str(i)]['cycle'] = -1
                self.struct[pattern_idx][str(i)]['ones in cycle'] = 0
                
                # Find which cycle this node belongs to
                for c in range(len(self.cycles[pattern_idx])):
                    if str(i) in self.cycles[pattern_idx][c]:
                        self.struct[pattern_idx][str(i)]['cycle'] = c
                        # Sum the first element of the pattern for all nodes in the cycle
                        self.struct[pattern_idx][str(i)]['ones in cycle'] = sum(
                            int(self.struct[pattern_idx][j]["pattern"][0]) 
                            for j in self.cycles[pattern_idx][c]
                        )
                        break

    def save_graph_data(self) -> None:
        """Save the augmented graph data back to the JSON file."""
        if self.struct is None:
            raise ValueError("No graph data to save. Load data first.")
        
        with open(self.graph_file_path, 'w') as json_file:
            json.dump(self.struct, json_file)

    def process(self) -> None:
        """
        Run the complete pipeline: load, detect cycles, augment, and save.
        """
        self.load_graph_data()
        self.augment_struct_with_cycles()
        self.save_graph_data()
        for pattern_idx in range(len(self.struct)):
            print(f"Pattern {pattern_idx}:")
            self.print_cycle_ones(Npat=pattern_idx)
