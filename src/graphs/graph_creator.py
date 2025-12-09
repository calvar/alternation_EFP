from __future__ import annotations

import json
import numpy as np

from itertools import combinations
from typing import Dict, List, Tuple, Optional, Sequence, Union

from config.config import PATHS


class StrategyGraphBuilder:
    """
    Analyse repeated‐action *patterns* (bit-strings) to infer each agent’s local
    decision rule (“strategy”) given a set of observable neighbour columns.

    Parameters
    ----------
    rng
        An explicit NumPy RNG (`np.random.Generator` or legacy
        `np.random.RandomState`).  If ``None`` (default) the class creates its
        own `np.random.default_rng()`.  Passing the RNG from the outside gives
        the caller full control over determinism and reproducibility.
    """

    def __init__(
        self,
        rng: Optional[Union[np.random.Generator, np.random.RandomState]] = None,
    ) -> None:
        self.patterns: List[Dict[str, str]] = self._load_patterns()
        self.N: int = len(self.patterns[0])  
        self.s = np.sum([int(self.patterns[0][i][0]) for i in self.patterns[0]])

        # Use caller-supplied RNG or make a fresh one
        self.rng: Union[np.random.Generator, np.random.RandomState] = (
            rng if rng is not None else np.random.default_rng()
        )

        # Every agent initially observes *all* others; adapt as needed.
        self._neighbour_mats: List[np.ndarray] = [
            np.tile(np.arange(self.N), (self.N, 1)) for _ in self.patterns
        ]
        self._graphs: Optional[List[Dict[int, Dict[str, object]]]] = None

    # ------------------------------------------------------------------ #
    #  Public API                                                        #
    # ------------------------------------------------------------------ #
    def build_graphs(
        self,
        shuffle: bool = True
    ) -> None:
        """
        Build a strategy graph for every pattern in ``self.patterns``.
        Returns a list (one element per pattern) with agent-level entries
        ''pattern'', ''neigh'', ''strat'', and ''input freq''.
        """
        if self._graphs is not None:
            return self._graphs                               # already built

        graphs: List[Dict[int, Dict[str, object]]] = []
        for pat, neigh_mat in zip(self.patterns, self._neighbour_mats):
            pattern_graph: Dict[int, Dict[str, object]] = {}
            for agent_idx in range(self.N):
                strat_tuple = self._get_strategy(
                    pattern=pat,
                    idx=agent_idx,
                    neighbour_mat=neigh_mat,
                    shuffle=shuffle,
                )

                pattern_graph[agent_idx] = {
                    "pattern": pat[str(agent_idx)],
                    "neigh":   strat_tuple[0] if strat_tuple else None,
                    "strat":   strat_tuple[1] if strat_tuple else None,
                    "input freq": strat_tuple[2] if strat_tuple else None,
                }
            graphs.append(pattern_graph)

        self._graphs = graphs
        
        graph_path = PATHS['graphs'] / f"graph_data_N{self.N:d}s{self.s:d}.json"
        with open(graph_path, 'w') as json_file:
          json.dump(graphs, json_file)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _filter_pattern(
        pattern: Dict[str, str],
        mask: Sequence[bool]
    ) -> Dict[str, str]:
        """Return a view of *pattern* restricted to columns where *mask* is True."""
        return {k: v for k, v in pattern.items() if mask[int(k)]}

    def _get_strategy(
        self,
        pattern: Dict[str, str],
        idx: int,
        neighbour_mat: np.ndarray,
        shuffle: bool = True,
    ) -> Optional[Tuple[Tuple[str, ...], Dict[str, str], Dict[str, int]]]:
        """
        Infer a deterministic mapping from observed neighbour columns to the
        agent’s next action.  Returns ``None`` if no stable mapping exists.
        """
        neighbours = neighbour_mat[idx].tolist()
        T = len(pattern[str(idx)])

        for subset_size in range(1, len(neighbours) + 1):
            combos = list(combinations(neighbours, subset_size)) # list of neighbors to pay attention to
            if shuffle:
                self.rng.shuffle(combos)                      # <-- uses caller's RNG
            
            for cols in combos:
                cols_sorted = sorted(cols)
                mask = [i in cols_sorted for i in range(self.N)]
                filtered = self._filter_pattern(pattern, mask)

                mapping: Dict[str, str] = {} # rules: if you see key -> do target
                counts: Dict[str, int] = {}  # how many times each key was observed
                consistent = True     # check if a single key maps to a single target

                for t in range(T):
                    key = "".join(filtered[str(c)][t] for c in cols_sorted)
                    target = pattern[str(idx)][(t + 1) % T]

                    if key in mapping:
                        if mapping[key] != target:
                            consistent = False
                            break
                        counts[key] += 1
                    else:
                        mapping[key] = target
                        counts[key] = 1

                if not consistent:
                    continue

                if len(set(mapping.values())) == 1:           # always-do-X rule
                    return (), {"any": next(iter(mapping.values()))}, {"any": 1}
                return tuple(map(str, cols_sorted)), mapping, counts

        return None  # no deterministic strategy found

    # ------------------------------------------------------------------ #
    #  Construction helpers                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_patterns() -> List[Dict[str, str]]:
        """
        Load and return the *patterns* list stored in a JSON file.

        The file must contain a JSON representation compatible with the
        expected structure (a list of dicts whose keys are agent-ids and
        whose values are binary strings).

        Examples
        --------
        >>> pats = StrategyGraphBuilder.load_patterns(
        ...     PATHS['patterns'] / 'patterns.json')
        """
        pattern_path = PATHS['patterns'] / 'patterns.json'

        with pattern_path.open("r", encoding="utf-8") as f:
            return json.load(f)