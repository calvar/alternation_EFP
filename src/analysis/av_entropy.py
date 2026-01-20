import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

from config.config import PATHS


class EntropyAnalyzer:
    """
    A class for analyzing entropy and information averages from graph data.
    
    This class provides methods to calculate probability distributions, entropy values,
    and average entropy information from graph structure data stored in JSON files.
    """
    
    def __init__(self):
        """
        Initialize the EntropyAnalyzer.
        """
        self._cached_data: Dict[str, dict] = {}
    
    @staticmethod
    def calculate_distribution(frequency: Dict[str, Union[int, float]]) -> Dict[str, float]:
        """
        Calculate probability distribution from frequency data.
        
        Args:
            frequency: Dictionary mapping keys to their frequencies
            
        Returns:
            Dictionary mapping keys to their probabilities
            
        Raises:
            ValueError: If frequency dictionary is empty or contains negative values
        """
        if not frequency:
            raise ValueError("Frequency dictionary cannot be empty")
        
        total = sum(frequency.values())
        if total <= 0:
            raise ValueError("Total frequency must be positive")
        
        if any(v < 0 for v in frequency.values()):
            raise ValueError("Frequency values cannot be negative")
        
        return {k: v / total for k, v in frequency.items()}
    
    @staticmethod
    def calculate_entropy(frequency: Dict[str, Union[int, float]]) -> float:
        """
        Calculate Shannon entropy from frequency data.
        
        Args:
            frequency: Dictionary mapping keys to their frequencies
            
        Returns:
            Shannon entropy in bits
            
        Raises:
            ValueError: If frequency data is invalid
        """
        try:
            distribution = EntropyAnalyzer.calculate_distribution(frequency)
            return -np.sum([p * np.log2(p) for p in distribution.values() if p > 0])
        except ValueError as e:
            raise ValueError(f"Cannot calculate entropy: {e}")
    
    def _load_graph_data(self, n: int, s: int) -> dict:
        """
        Load graph data from JSON file with caching.
        
        Args:
            n: Number of nodes
            s: Parameter s
            
        Returns:
            Loaded graph structure data
            
        Raises:
            FileNotFoundError: If the data file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        filename = f'graph_data_N{n:d}s{s:d}.json'
        cache_key = f"{n}_{s}"
        
        if cache_key in self._cached_data:
            return self._cached_data[cache_key]
        
        file_path = PATHS['graphs'] / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Graph data file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self._cached_data[cache_key] = data
            return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e}")
    
    def calculate_average_info_per_node(self, pattern_data: dict, n: int) -> float:
        """
        Calculate average input information per node for a pattern.
        
        Args:
            pattern_data: Pattern data containing node information
            n: Total number of nodes
            
        Returns:
            Average input information per node
        """
        total_info = sum(len(node_data['neigh']) for node_data in pattern_data.values())
        return total_info / n
    
    def calculate_average_entropy_per_node(self, pattern_data: dict, n: int) -> float:
        """
        Calculate average input entropy per node for a pattern.
        
        Args:
            pattern_data: Pattern data containing node frequency information
            n: Total number of nodes
            
        Returns:
            Average input entropy per node
        """
        total_entropy = sum(
            EntropyAnalyzer.calculate_entropy(node_data['input freq']) 
            for node_data in pattern_data.values()
        )
        return total_entropy / n
    
    def compute_entropy_info(self, n: int, s: int, verbose: bool = False) -> Tuple[List[float], List[float]]:
        """
        Calculate average entropy and information for all patterns in the dataset.
        
        Args:
            n: Number of nodes
            s: Parameter s
            verbose: If True, print intermediate results
            
        Returns:
            Tuple containing:
                - List of average input information per node for each pattern
                - List of average entropy of inputs per node for each pattern
                
        Raises:
            FileNotFoundError: If the graph data file doesn't exist
            ValueError: If the data contains invalid values
        """
        struct = self._load_graph_data(n, s)
        
        info_averages = []
        entropy_averages = []
        
        for pattern_idx in range(len(struct)):
            pattern_data = struct[pattern_idx]
            
            # Calculate average input information per node
            avg_info = self.calculate_average_info_per_node(pattern_data, n)
            info_averages.append(avg_info)
            
            if verbose:
                print(f'Pattern {pattern_idx}: Average input information (bandwidth) per node: {avg_info:.2f}')
            
            # Calculate average input entropy per node
            avg_entropy = self.calculate_average_entropy_per_node(pattern_data, n)
            entropy_averages.append(avg_entropy)
            
            if verbose:
                print(f'Pattern {pattern_idx}: Average entropy of inputs per node: {avg_entropy:.2f}')
        
        return info_averages, entropy_averages
    
    def clear_cache(self) -> None:
        """Clear the internal data cache."""
        self._cached_data.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """
        Get information about cached data.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_datasets': len(self._cached_data),
            'cache_keys': list(self._cached_data.keys())
        }


