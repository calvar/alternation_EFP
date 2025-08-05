import json
import numpy as np

from pathlib import Path
from typing import Dict, List, Sequence, Optional, Union


class PatternGenerator:
    """Generate binary patterns with optional column and row permutations.

    A *pattern* is built by sliding a window of ones (size ``step``) across a
    vector of zeros (length ``N``). Each distinct position of the window
    contributes one *row* to the pattern, and the procedure stops once the
    initial window re‑appears.

    The internal representation is *column‑centric*: a ``dict`` that maps each
    column index to a list of character strings (``'0'`` or ``'1'``), where the
    list length equals the number of rows.  Entire columns or rows can then be
    permuted independently to create additional variants.

    Parameters
    ----------
    N : int
        Length of each pattern row (number of columns).
    step : int
        Size of the sliding window of ones. Must satisfy ``0 < step <= N``.
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
        N: int,
        step: int,
        num_patterns: int,
        permute_columns: bool = False,
        permute_rows: bool = False,
        rng: Optional[np.random.Generator] = None,
    ) -> None:
        if not (0 < step <= N):
            raise ValueError("`step` must be in the interval (0, N].")
        self.N = N
        self.step = step
        if num_patterns <= 0:
            raise ValueError("`n` must be a positive integer.")
        self.num_patterns = num_patterns
        self.permute_columns = permute_columns
        self.permute_rows = permute_rows
        # Create a dedicated random generator for this instance
        self.rng = rng or np.random.default_rng()

        # Cache for the most recently generated pattern
        self._pattern: Dict[int, List[str]] = {}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _swap_columns(self, i: int, j: int) -> None:
        """Swap columns *i* and *j* in‑place inside ``self._pattern``."""
        self._pattern[i], self._pattern[j] = self._pattern[j], self._pattern[i]

    def _swap_rows(self, i: int, j: int) -> None:
        """Swap entries *i* and *j* across every column (row permutation)."""
        for col in self._pattern.values():
            col[i], col[j] = col[j], col[i]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self) -> Dict[int, List[str]]:
        """Create the basic pattern.

        Returns
        -------
        Dict[int, List[str]]
            The generated pattern. Keys are column indices; values are lists of
            ``'0'``/``'1'`` strings of equal length.
        """
        # Step 1 – Build the base pattern as a list of rows -------------
        rows: List[Sequence[str]] = []
        initial_window = list(range(self.step))
        window = initial_window
        offset = 0
        while offset == 0 or window != initial_window:
            rows.append(
                ["1" if idx in window else "0" for idx in range(self.N)]
            )
            offset += self.step
            window = [(offset + idx) % self.N for idx in range(self.step)]

        # Step 2 – Convert to column‑centric representation -------------
        self._pattern = {
            col: [row[col] for row in rows] for col in range(self.N)
        }

        # Step 3 – Optional permutations -------------------------------
        if self.permute_columns:
            for _ in range(self.rng.integers(0, self.N)):
                a, b = self.rng.integers(0, self.N, size=2)
                self._swap_columns(int(a), int(b))

        if self.permute_rows:
            num_rows = len(rows)
            for _ in range(self.rng.integers(0, num_rows)):
                a, b = self.rng.integers(0, num_rows, size=2)
                self._swap_rows(int(a), int(b))

        return self._pattern

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