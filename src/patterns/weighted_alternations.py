import json
import numpy as np
import string

from pathlib import Path
from typing import Dict, List, Sequence, Optional, Union


class WeightedPatternGenerator:
    """Generate weighted binary patterns with optional column and row permutations.

    The internal representation is *column‑centric*: a ``dict`` that maps each
    column index to a list of character strings (``'0'`` or ``'1'``), where the
    list length equals the number of rows.  Entire columns or rows can then be
    permuted independently to create additional variants.

    Parameters
    ----------
    procs : Dict[int, int]
        Dictionary where each key is a process(agent) index and each value is the weight, that is,
        the number of times the process(agent) should be active (1) in the pattern.
    spots : int
        Number of ones in each pattern row. Must satisfy ``0 < spots <= N``.
    num_patterns : int
            Number of different patterns to produce. Must be > 0.
    permute_columns : bool, default ``False``
        If *True*, swap a random number of column pairs after the base pattern
        is built.
    permute_rows : bool, default ``False``
        If *True*, swap a random number of row pairs after the base pattern is
        built.
    rng : numpy.random.Generator, optional
            Random‑number generator for reproducibility.  If *None*,
            ``np.random.default_rng()`` is used.
    """

    def __init__(
        self,
        procs: Dict[int, int],
        spots: int,
        num_patterns: int,
        permute_columns: bool = False,
        permute_rows: bool = False,
        rng: Optional[np.random.Generator] = None,
    ) -> None:
        self.procs = procs
        self.N = len(procs)
        if not (0 < spots <= self.N):
            raise ValueError("`spots` must be in the interval (0, N].")
        self.spots = spots
        if num_patterns <= 0:
            raise ValueError("`n` must be a positive integer.")
        self.num_patterns = num_patterns
        self.permute_columns = permute_columns
        self.permute_rows = permute_rows
        # Create a dedicated random generator for this instance
        self.rng = rng or np.random.default_rng()
    
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def swap_columns(self, i: int, j: int, pattern: Dict[str, List[str]]) -> None:
        """Swap columns *i* and *j* in‑place inside ``self._pattern``."""
        pattern[i], pattern[j] = pattern[j], pattern[i]

    def swap_rows(self, i: int, j: int, pattern: Dict[str, List[str]]) -> None:
        """Swap entries *i* and *j* across every column (row permutation)."""
        for col in pattern.values():
            col[i], col[j] = col[j], col[i]
    
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self) -> Dict[str, List[str]]:
        """Create the basic weighted pattern.

        Returns
        -------
        Dict[str, List[str]]
            The generated pattern. Keys are process indices; values are lists of
            ``'0'``/``'1'`` strings of equal length.
        """

        # Step 1 – Build the base pattern as a 1D array whose ordering represents the turns. -------------
        # The number of times each process appears in the list is determined by its weight in `procs`,
        # and it is repeated until the total length is a multiple of `spots` (the number of active processes per turn).
        D = self.procs.copy()
        l = []
        c = 0
        while True:
            if D[c] > 0:
                l.append(c)
                D[c] -= 1
            c = (c+1) % len(D)
            if sum(D.values()) == 0:
                break
        n = 1
        while (n*len(l))%self.spots != 0:
            n += 1
        ll = n*l

        # Step 2 - Split the list into batches of size `spots` (the number of active processes per turn), 
        # to create the pattern rows, taking care that no process appears more than once in each batch.
        sol = []
        count = 0
        while count < len(ll):
            batch = []
            for i in range(self.spots):
                if count < len(ll):
                    u = 1
                    while ll[count] in batch:
                        d = ll[count]
                        ll[count] = ll[(count+u) % len(ll)]
                        ll[(count+u) % len(ll)] = d
                        u += 1
                    batch.append(ll[count])
                    count += 1
            sol.append(batch)
        sol = np.array(sol)
        #print(sol)

        # Step 3 - Make sure that no two rows are identical, by swapping an element of one of the 
        # repeated rows with the same element of a random row that is not repeated.
        repeated = []
        for i in range(len(sol)-1):
            for j in range(i+1, len(sol)):
                if np.array_equal(sorted(sol[i]), sorted(sol[j])):
                    repeated.append((i, j))
        #print("Repeated rows:", repeated)
        for i, j in repeated:
            # Swap element a of row j with a random row k that is not i or j
            k = self.rng.integers(0, len(sol))
            a = self.rng.integers(0, len(sol[0]))
            while (k == i or k == j) or ((sol[k][a] in sol[j]) or (sol[j][a] in sol[k])):
                k = self.rng.integers(0, len(sol))
                a = self.rng.integers(0, len(sol[0]))
            sol[j][a], sol[k][a] = sol[k][a], sol[j][a]
        #print(sol)

        # for d in D:
        #    v = np.sum(sol == d)
        #    print(f"Value {d}: {v}")

        # Step 4 - Convert to column‑centric representation, where each value is the pattern for an agent through time -------------
        rows = []
        for c in sol:
            v = ["1" if d in c else "0" for d in D]
            rows.append(v)
        #print(rows)
        pattern = {
            col: [row[col] for row in rows] for col in range(len(D))
        }

        # Step 5 – Optional permutations -------------------------------
        if self.permute_columns:
            for _ in range(self.rng.integers(0, len(D))):
                a, b = self.rng.integers(0, len(D), size=2)
                self.swap_columns(int(a), int(b), pattern)

        if self.permute_rows:
            num_rows = len(rows)
            for _ in range(self.rng.integers(0, num_rows)):
                a, b = self.rng.integers(0, num_rows, size=2)
                self.swap_rows(int(a), int(b), pattern)
        
        # Step 6 - expand the pattern by creating a new row for each '1' in the original pattern, 
        # where the new row has a '1' in the same position and '0's elsewhere. This way, 
        # we get a pattern where each node is active in exactly one turn, and the number of 
        # rows equals the total number of active turns across all processes.
        num_to_letter_map = dict(zip(range(0,26), string.ascii_lowercase))
        expanded = {}
        for i in pattern:
            count = 0
            for j in range(len(pattern[i])):
                if pattern[i][j] == "1":
                    v = ["1" if k == j else "0" for k in range(len(pattern[i]))]
                    expanded[str(i) + num_to_letter_map[count]] = v
                    count += 1
        
        return expanded
    

    def generate_many(self) -> List[Dict[int, List[str]]]:
        """Generate *n* independent patterns and return them as a list.

        Examples
        --------
        >>> gen = PatternGenerator(7, 3, permute_columns=True, permute_rows=True)
        >>> patterns = gen.generate_many(10)  # 10 different patterns
        """
        return [self.generate() for _ in range(self.num_patterns)]
    
    def save(self, filepath: Union[str, Path]) -> None:
        """Save a pattern dictionary to *filepath* in JSON format.

        By default, the method saves the most recently generated pattern.
        A custom *patterns* dictionary (e.g., a list of multiple patterns) can
        be supplied instead.
        """
        patterns = self.generate_many()

        file = Path(filepath)
        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("w") as f:
            json.dump(patterns, f)
    
    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------
    @property
    def pattern(self) -> Dict[int, List[str]]:
        """Return the most recently generated pattern.

        Raises
        ------
        RuntimeError
            If ``generate`` has not been called yet.
        """
        if not self._pattern:
            raise RuntimeError("No pattern generated yet. Call `generate()`.")
        return self._pattern