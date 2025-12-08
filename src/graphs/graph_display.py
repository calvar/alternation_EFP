import json
import random
import networkx as nx

import matplotlib.colors as mcolors
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from config.config import PATHS


class GraphVisualizer:
    """Class to read graph data and generate interactive HTML visualizations."""

    def __init__(self, num_nodes: int, num_steps: int) -> None:
        """
        Initialize the GraphVisualizer.
        
        Args:
            num_nodes: Number of nodes in the graph
            num_steps: Number of steps in the graph evolution
        """
        self.struct = None
        self.N = num_nodes
        self.s = num_steps

        self.graph_data_path = PATHS['graphs'] / f"graph_data_N{self.N:d}s{self.s:d}.json"
        self.output_html_path = PATHS['html'] / f"graph_N{self.N:d}s{self.s:d}.html"
        
        # Setup colors and shapes
        named_colors = mcolors.CSS4_COLORS
        self.color_names = list(named_colors.keys())
        random.seed(1234)
        random.shuffle(self.color_names)
        self.shape_names = ['dot', 'diamond', 'square', 'triangle', 'star', 'triangleDown']
        
    def load_graph_data(self) -> None:
        """Load graph data from JSON file."""
        with open(self.graph_data_path, 'r') as f:
            self.struct = json.load(f)
            
    def bin_to_decimal(self, bin_str: str) -> int:
        """Convert binary string to decimal."""
        return int(bin_str, 2)
    
    def get_color(self, bin_str: str) -> str:
        """Get color based on binary string."""
        decimal = self.bin_to_decimal(bin_str)
        return self.color_names[decimal % len(self.color_names)]
    
    def get_shape(self, bin_str: str) -> str:
        """Get shape based on binary string."""
        decimal = self.bin_to_decimal(bin_str)
        return self.shape_names[decimal % len(self.shape_names)]
    
    def build_graph_data(self, pattern_index: int = 0) -> Tuple[List[Tuple[str, str]], Dict[str, str], Dict[str, str], Dict[str, str]]:
        """
        Build graph data structures for visualization.
        
        Args:
            pattern_index: Index of the pattern to visualize
            
        Returns:
            Tuple of (edges, edge_colors, node_colors, node_shapes)
        """
        edges = []
        e_colors = {}
        n_colors = {}
        n_shapes = {}
        
        for n1 in self.struct[pattern_index]:
            # Set node colors and shapes based on pattern
            pattern_str = ''.join(i for i in self.struct[pattern_index][n1]["pattern"])
            n_colors[n1] = self.get_color(pattern_str)
            n_shapes[n1] = self.get_shape(pattern_str)
            
            # Build edges
            for n2 in self.struct[pattern_index][str(n1)]["neigh"]:
                if len(self.struct[pattern_index][str(n1)]["strat"]) > 1:
                    edges.append((n2, n1))
                    
                    # Determine edge color based on strategy
                    copy_strat = False
                    if len(self.struct[pattern_index][str(n1)]["strat"]) == 2:
                        copy_strat = (
                            self.struct[pattern_index][str(n1)]["strat"]['0'] == '0' and
                            self.struct[pattern_index][str(n1)]["strat"]['1'] == '1'
                        )
                        if copy_strat:
                            e_colors[f'{n2}-{n1}'] = 'darkturquoise'
                        else:
                            e_colors[f'{n2}-{n1}'] = 'black'
                    else:
                        e_colors[f'{n2}-{n1}'] = 'black'
        
        return edges, e_colors, n_colors, n_shapes
    
    def create_network(self, edges: List[Tuple[str, str]], 
                      e_colors: Dict[str, str], 
                      n_colors: Dict[str, str], 
                      n_shapes: Dict[str, str],
                      num_nodes: int,
                      width: str = "400px",
                      height: str = "400px") -> Network:
        """
        Create a pyvis Network object.
        
        Args:
            edges: List of edge tuples
            e_colors: Dictionary of edge colors
            n_colors: Dictionary of node colors
            n_shapes: Dictionary of node shapes
            num_nodes: Number of nodes in the graph
            
        Returns:
            Configured pyvis Network object
        """
        # Create directed graph
        DG = nx.DiGraph()
        DG.add_nodes_from([str(i) for i in range(num_nodes)])
        DG.add_edges_from(edges)
        for node in DG.nodes:
            DG.nodes[node]['color'] = n_colors[node]
        
        # Create pyvis network
        dnet = Network(height, width, notebook=False, directed=True)
        dnet.from_nx(DG)
        
        # Apply colors and shapes
        for edge in dnet.edges:
            edge['color'] = e_colors[f"{edge['from']}-{edge['to']}"]
        for node in dnet.nodes:
            node['color'] = {'background': n_colors[node['id']], 'border': 'black'}
            node['shape'] = n_shapes[node['id']]
        
        return dnet
    
    def generate_html(self, pattern_index: int = 0, 
                     width: str = "400px", 
                     height: str = "400px",
                     physics: bool = True) -> Tuple[Network, str]:
        """
        Generate HTML visualization for a specific pattern.
        display(widgets.HTML(f"<b>Pattern {i} Visualization:</b>"))
        Args:
            pattern_index: Index of the pattern to visualize
            width: Width of the visualization
            height: Height of the visualization
            physics: Whether to enable physics simulation
            
        Returns:
            Path to the generated HTML file
        """
        if self.struct is None:
            self.load_graph_data()
        
        # Determine number of nodes from the data
        num_nodes = len(self.struct[pattern_index])
        
        # Build graph data
        edges, e_colors, n_colors, n_shapes = self.build_graph_data(pattern_index)
        
        # Create network using helper
        dnet = self.create_network(
            edges=edges,
            e_colors=e_colors,
            n_colors=n_colors,
            n_shapes=n_shapes,
            num_nodes=num_nodes,
            width=width,
            height=height,
        )
        
        # Toggle physics
        dnet.toggle_physics(physics)
        
        # Determine output path
        if self.output_html_path is None:
            # Extract N and s from filename if possible
            filename = self.graph_data_path.stem
            output_filename = filename.replace('graph_data', 'graph') + '.html'
            output_path = self.graph_data_path.parent.parent / 'html' / output_filename
        else:
            output_path = self.output_html_path
        
        ## Generate HTML
        #dnet.show(str(output_path))
        
        return dnet, str(output_path)
    
    def generate_all_patterns(self, width: str = "400px", 
                             height: str = "400px",
                             physics: bool = True) -> List[str]:
        """
        Generate HTML visualizations for all patterns in the graph data.
        
        Args:
            width: Width of the visualization
            height: Height of the visualization
            physics: Whether to enable physics simulation
            
        Returns:
            List of paths to generated HTML files
        """
        if self.struct is None:
            self.load_graph_data()
        
        nets = []
        output_files = []
        num_patterns = len(self.struct)
        
        for pattern_idx in range(num_patterns):
            # Modify output path for multiple patterns
            # Append pattern index to provided path
            dnet, output_path = self.generate_html(pattern_idx, width, height, physics)
            output_path = Path(str(self.output_html_path).replace('.html', f'_pattern{pattern_idx}.html'))
            
            # Generate for this pattern
            temp_output = self.output_html_path
            self.output_html_path = output_path
            output_file = self.generate_html(pattern_idx, width, height, physics)
            self.output_html_path = temp_output
            
            nets.append(dnet)
            output_files.append(output_path)
        
        return nets, output_files
