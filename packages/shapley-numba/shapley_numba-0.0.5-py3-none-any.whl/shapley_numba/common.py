"""Common functions for shapley_numba.

Mostly subset manipulation.
"""

from typing import Generator, Iterator

import numba
import numpy as np
from numpy.typing import NDArray

from shapley_numba import CoalitionType

__all__ = [
    'subsets',
    'subsets_of_subset',
    'combs_jit',
    'combs',
    'subsets_of_fixed_size',
    'mask_to_subset',
    'add_subset_size',
]


@numba.jit(nopython=True)
def subsets(num_players: int | np.int32, self_included: bool = True):
    """Compute subsets of set with num_players number of elements.

    Parameters
    ----------
    num_players : int
        Number of elements in the set.

    self_included : bool, default True
        Whether to include the total set.

    Returns
    -------
    subsets : generator
        Generator of subsets.
        Each subset is a numpy array of length num_players
        with value 0, 1 depending if element is present
        in the subset of not

    """
    limit = 2**num_players
    if not self_included:
        limit -= 1
    for subset_int in range(limit):
        subset = np.zeros(num_players, dtype=np.int32)
        i = 0
        while subset_int > 0:
            subset[i] = subset_int % 2
            i += 1
            subset_int = subset_int >> 1
        yield subset


@numba.jit(nopython=True)
def subsets_of_subset(subset: CoalitionType, self_included: bool = True):
    """Compute subsets of subset.

    Parameters
    ----------
    subset : numpy array
        Subset to compute subsets of.

    self_included : bool
        Whether to include the subset itself.



    Returns
    -------
    subsets : generator
        Generator of subsets.
        Each subset is a numpy array of length of the subset

    """
    num_players = len(subset)
    num_elements = np.sum(subset)
    mask = num_players * np.ones(num_players, dtype=np.int32)
    mask_index = 0
    for ind in range(num_players):
        if subset[ind] == 1:
            mask[mask_index] = ind
            mask_index += 1
    for subsusbset in subsets(num_elements, self_included=self_included):
        new_subset = np.zeros(num_players, dtype=np.int32)
        for ind in range(num_elements):
            new_subset[mask[ind]] = subsusbset[ind]
        yield new_subset


@numba.jit(nopython=True, cache=True)
def combs_jit(
    num_players: int, dtype: type = np.int32
) -> NDArray[np.int16] | NDArray[np.int32] | NDArray[np.int64]:
    """Build choose(num_players, k + 1) array in numba.

    Reimplemented because scipy is not compiled in numba.

    Returns
    -------
    np.array of int32 of length num_players - 1,
    where k'th element is choose(num_players, k + 1)

    """
    combs: NDArray[np.int16] | NDArray[np.int32] | NDArray[np.int64] = np.zeros(
        num_players - 1, dtype=dtype
    )
    combs[0] = num_players  # choose(num_players, 1)
    for n_coalition in range(1, num_players - 1):
        combs[n_coalition] = (
            (num_players - n_coalition) * combs[n_coalition - 1] // (n_coalition + 1)
        )
    return combs


@numba.jit(nopython=True, cache=True)
def combs(num_players: int, player: int) -> int:
    """Return choose(num_players, player).

    Reimplemented because scipy is not compiled in numba.

    """
    if player < 0 or player > num_players:
        return 0
    if player == 0 or player == num_players:
        return 1
    if player > num_players // 2:
        player = num_players - player

    res = 1
    for i in range(player):
        res = res * (num_players - i) // (i + 1)
    return res


@numba.jit(nopython=True)
def mask_to_subset(mask: NDArray[np.int32]) -> CoalitionType:
    """Convert mask to subset.

    Parameters
    ----------
    mask : numpy array
        Mask to convert to subset.

    Returns
    -------
    subset : numpy array
        Subset corresponding to the mask.

    """
    num_players = len(mask)
    subset = np.zeros(num_players, dtype=np.int32)
    ind = 0
    while mask[ind] != -1:
        subset[mask[ind]] = 1
        ind += 1
    return subset


@numba.jit(nopython=True)
def add_subset_size(
    subsets_iter: Iterator[NDArray[np.int32]],
) -> Generator[tuple[CoalitionType, np.int32], None, None]:
    """Subset with number of elements in each subset."""
    for subset in subsets_iter:
        yield subset, np.sum(subset)


@numba.jit(nopython=True)
def subsets_of_fixed_size(num_players: int, size: int):
    """Compute subsets of fixed size using iterative combinatorial generation.

    This uses a standard combinatorial algorithm to generate all k-combinations
    of n elements without recursion, making it compatible with Numba's nopython mode.

    Parameters
    ----------
    num_players : int
        Number of players in the game.
    size: int
        Size of the generated subset

    Yields
    ------
    NDArray[np.int32]
        Each subset as a 1D array of length num_players

    """
    if size == 0:
        yield np.zeros(num_players, dtype=np.int32)
        return

    if size > num_players:
        return

    # Initialize indices to [0, 1, 2, ..., size-1]
    indices = np.arange(size, dtype=np.int32)

    while True:
        # Generate current subset
        subset = np.zeros(num_players, dtype=np.int32)
        for i in range(size):
            subset[indices[i]] = 1
        yield subset

        # Find the rightmost index that can be incremented
        i = size - 1
        while i >= 0 and indices[i] == num_players - size + i:
            i -= 1

        # If no index can be incremented, we're done
        if i < 0:
            break

        # Increment index i
        indices[i] += 1

        # Reset all indices to the right of i
        for j in range(i + 1, size):
            indices[j] = indices[j - 1] + 1
