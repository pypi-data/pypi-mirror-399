""" Sort With Developer's SortingChangelist FilePatterns.
"""
from typing import Callable, Generator

from changelist_sort.data.change_data import ChangeData
from changelist_sort.data.changelist_map import ChangelistMap
from changelist_sort.data.list_key import ListKey
from changelist_sort.data.sorting_changelist import SortingChangelist
from changelist_sort.sorting import file_sort, module_sort
from changelist_sort.sorting.module_type import ModuleType


def get_sorting_functions(
    cl_map: ChangelistMap,
    sorting_config: list[SortingChangelist] | None,
) -> tuple[Callable, Callable]:
    """ Obtain the Sorting Functions for the Changelist Map Sorting Algorithm.

**Parameters:**
 - cl_map (ChangelistMap): The Map object to use with the sorting functions.
 - sorting_config (list[SortingChangelist]?): The list of Changelist sorting criteria. If none, returns module_sort functions.

**Returns:**
 tuple - The Sorting Functions.
    """
    if sorting_config is None or len(sorting_config) < 1:
        return (
            lambda key, cd: module_sort.is_sorted_by_module(key, cd),
            lambda cd: module_sort.sort_file_by_module(cl_map, cd),
        )
    return (
        lambda key, cd: is_sorted_by_developer(key, cd, sorting_config),
        lambda cd: sort_file_by_developer(cl_map, cd, sorting_config)
    )


def sort_file_by_developer(
    cl_map: ChangelistMap,
    file: ChangeData,
    sorting_config: list[SortingChangelist],
) -> bool:
    """ Apply the SortingChangelist FilePattern Settings to Sort a single File into the Changelist Map.
 - Filters Patterns by matching ModuleType before checking files.
 - Fallback to Module Sort.

**Parameters:**
 - cl_map (ChangelistMap): The ChangelistMap to sort with.
 - file (ChangeData): The ChangeData describing a file's sorting information.
 - sorting_config (list[SortingChangelist]): The list of Changelist sorting criteria.

**Returns:**
 bool - The result of the sorting operation on this specific file.
    """
    for scl_pattern in _filter_by_module(
        file_sort.get_module_type(file), sorting_config
    ):
        if scl_pattern.check_file(file): # Pattern Matched.
            if (cl := cl_map.search(scl_pattern.list_key.key)) is None:
                cl = cl_map.create_changelist(scl_pattern.list_key)
            cl.changes.append(file) # Add File to Changelist.
            return True
    return module_sort.sort_file_by_module(cl_map, file)


def is_sorted_by_developer(
    changelist_key: ListKey,
    file: ChangeData,
    sorting_config: list[SortingChangelist],
) -> bool:
    """ Determines if this File matches the ChangeList Key or Name.
 - Finds the First SortingCL FilePattern match.
 - Fallback to Module Sort.

**Parameters:**
 - changelist_key (ListKey): The key of the Changelist to compare with the file and sorting criteria.
 - file (ChangeData): The ChangeData describing a file's sorting information.
 - sorting_config (list[SortingChangelist]): The list of Changelist sorting criteria.

**Returns:**
 bool - The result of the sorting operation on this specific file.
    """
    for scl_pattern in _filter_by_module(
        file_sort.get_module_type(file), sorting_config
    ):
        if scl_pattern.check_file(file):
            # Pattern Matched. It is either already sorted, or needs to be.
            # - Temporary: Allow matching CL Names, even if key does not match.
            return scl_pattern.list_key.key == changelist_key.key or\
                scl_pattern.list_key.changelist_name == changelist_key.changelist_name
    # Fallback to Module Sort
    return module_sort.is_sorted_by_module(changelist_key, file)


def _filter_by_module(
    module_type: ModuleType | None,
    sorting_cl_list: list[SortingChangelist],
) -> Generator[SortingChangelist, None, None]:
    """ Filter Sorting Changelists by ModuleType.
 - This function filters a list of SortingChangelists based on the provided `module_type` argument.
 - SortingCL with a None ModuleType always pass through the filter. This is necessary to preserve file pattern order.
 - When None is passed as ModuleType argument, only SortingCL with None ModuleType pass through.

**Parameters:**
 - module_type (ModuleType?): The target module type to filter by. If None, only SortingChangelists with a None ModuleType will be included.
 - sorting_cl_list (list[SortingChangelist]): The list of SortingChangelists to filter.

**Yields:**
 SortingChangelist - Only the Changelist criteria that matches the ModuleType. May be empty.
    """
    if module_type is None:
        yield from filter(
            lambda scl: scl.module_type is None,
            sorting_cl_list
        )
    else:
        yield from filter(
            lambda scl: scl.module_type is None or scl.module_type == module_type,
            sorting_cl_list
        )
