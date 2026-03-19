from __future__ import annotations

import numpy as np
import json
from pathlib import Path
from typing import Dict, List

from config.config import PATHS


class EquitableNode:
    """Represents a node in the equitable graph with pattern and strategy information."""
    
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


class EquitableWeightedAgent:
    def __init__(self, 
                 id: str,
                 weight: int
                 ) -> None:
        self.id: str = id
        self.weight: int = weight
        self.nodes: List[EquitableNode] = []

    def __str__(self) -> str:
        return f"Agent: {self.id}\n weight: {self.weight}\n nodes: {[node.id for node in self.nodes]}"
    

class WeightedGraphCreator:
    """Creates and manages equitable weighted graphs with specified parameters."""
    
