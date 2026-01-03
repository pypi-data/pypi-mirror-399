""" Sorting Package Top Level Methods.
 - sort: Applies the SortingChangelist patterns to changelist_data input.
 - sort_with_mode: Select a SortMode from the built-in enum options.
"""
from typing import Iterable, Generator

from changelist_data import Changelist

from changelist_sort.data import expand_cl_iterable, compact_cl_iterable
from changelist_sort.data.sorting_changelist import SortingChangelist
from changelist_sort.sorting.map_sort import mode_sort, map_sort
from changelist_sort.sorting.sort_mode import SortMode


def sort(
    initial_list: Iterable[Changelist],
    sorting_config: list[SortingChangelist],
    filter_empty: bool,
) -> Generator[Changelist, None, None]:
    """ Apply SortingChangelists Patterns to a collection of changelist_data Changelists.

**Parameters:**
 - initial_list (list[ChangelistData]): The list of Changelists to be sorted.
 - sorting_config (list[SortingChangelist]): Changelist sorting patterns.
 - filter_empty (bool): Whether to filter empty changelists from the generated results.

**Yields:**
 Changelist - The sorted Changelists.
    """
    cl_map = map_sort(
        initial_list=expand_cl_iterable(initial_list),
        sorting_config=sorting_config
    )
    yield from compact_cl_iterable(
       cl_map.generate_nonempty_lists() if filter_empty else cl_map.generate_lists()
    )


def sort_with_mode(
    initial_list: Iterable[Changelist],
    mode: SortMode,
    filter_empty: bool,
) -> Generator[Changelist, None, None]:
    """ Apply a SortMode Changelist algorithm built-in to the program (no config).

**Parameters:**
 - initial_list (list[ChangelistData]): The list of Changelists to be sorted.
 - sort_mode (SortMode): The SortMode determining which sort rules to apply.
 - filter_empty (bool): Whether to filter empty changelists from the generated results.

**Yields:**
 Changelist - The sorted Changelists.
    """
    cl_map = mode_sort(
        initial_list=expand_cl_iterable(initial_list),
        sort_mode=mode,
    )
    yield from compact_cl_iterable(
        cl_map.generate_nonempty_lists() if filter_empty else cl_map.generate_lists()
    )
