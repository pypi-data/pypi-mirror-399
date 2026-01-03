""" Apply The Changelist Map Sorting Algorithm.
 - map_sort: Sort ChangelistData with SortingConfig.
 - mode_sort: Sort ChangelistData using a built-in SortMode.
"""
from typing import Iterable, Callable

from changelist_sort.data.changelist_data import ChangelistData
from changelist_sort.data.changelist_map import ChangelistMap
from changelist_sort.data.sorting_changelist import SortingChangelist
from changelist_sort.sorting import module_sort, source_set_sort
from changelist_sort.sorting.developer_sort import get_sorting_functions
from changelist_sort.sorting.list_sort import generate_unsorted_change_data
from changelist_sort.sorting.sort_mode import SortMode


def map_sort(
    initial_list: Iterable[ChangelistData],
    sorting_config: list[SortingChangelist],
) -> ChangelistMap:
    """ Sort The Changelists using the SortingConfig and the ChangelistMap.

**Parameters:**
 - initial_list (Iterable[ChangelistData]): The Changelists before they are sorted.
 - sorting_config (list[SortingChangelist]): The changelist sorting criteria.

**Returns:**
 ChangelistMap - A data container class for the sorted changelists.
    """
    cl_map = ChangelistMap()
    _sort_it_out(
        cl_map, initial_list, get_sorting_functions(cl_map, sorting_config)
    )
    return cl_map


def mode_sort(
    initial_list: Iterable[ChangelistData],
    sort_mode: SortMode,
) -> ChangelistMap:
    """ Sort Changelists using ChangelistMap and built-in SortMode configurations.

**Parameters:**
 - initial_list (Iterable[ChangelistData]): The Changelists before they are sorted.
 - sort_mode (SortMode): The selected built-in sorting configuration.

**Returns:**
 ChangelistMap - A data container class for the sorted changelists.
    """
    cl_map = ChangelistMap()
    _sort_it_out(
        cl_map, initial_list, _get_sort_mode_functions(cl_map, sort_mode)
    )
    return cl_map


def _sort_it_out(
    cl_map: ChangelistMap,
    unsorted_cl_data: Iterable[ChangelistData],
    sorting_functions: tuple[Callable, Callable],
):
    """ Changelist Map Sorting Algorithm.

**Parameters:**
 - cl_map (ChangelistMap): The ChangelistMap Data object for storing and searching Changelists efficiently.
 - unsorted_cl_data (Iterable[ChangelistData]): The unsorted Changelist Data iterable to be processed.
 - sorting_functions (tuple): The Sorting Functions to use in the Changelist Map Sort Algorithm.
    """
    unsorted_cd = []
    for cl in unsorted_cl_data:
        if not cl_map.insert(cl):
            _handle_map_insertion_error(cl_map, cl)
        unsorted_cd.extend(
            generate_unsorted_change_data(cl, sorting_functions[0])
        )
    for cd in unsorted_cd:
        sorting_functions[1](cd)
    # Sort Files in Lists
    for cl in cl_map.generate_nonempty_lists():
        cl.changes.sort(key=lambda cd: cd.sort_path)


def _get_sort_mode_functions(
    cl_map: ChangelistMap,
    sort_mode: SortMode,
):
    """ Gets Sorting Functions for built-in sort configurations.

**Parameters:**
 - cl_map (ChangelistMap): The Changelist Map object.
 - sort_mode (SortMode): The Sort Mode Enum.
    """
    m_sort = source_set_sort.sort_by_source_set if sort_mode == SortMode.SOURCESET else module_sort.sort_file_by_module
    return (
        source_set_sort.is_sorted_by_source_set if sort_mode == SortMode.SOURCESET else module_sort.is_sorted_by_module,
        lambda cd: m_sort(cl_map, cd)
    )


def _handle_map_insertion_error(
    cl_map: ChangelistMap,
    failure_cl: ChangelistData,
):
    """ Using the given parameters, produce an error message and exit.

**Raises:**
 SystemExit - containing error information.
    """
    if (existing_cl := cl_map.search(failure_cl.list_key.key)) is not None:
        exit(f"Failed to Insert Changelist(name={failure_cl.list_key.changelist_name}) due to key conflict with Changelist(name={existing_cl.list_key.changelist_name}).")
    elif cl_map.contains_id(failure_cl.id):
        exit(f"Failed to Insert Changelist(name={failure_cl.list_key.changelist_name}) due to id conflict (id={failure_cl.id}).")
    else:
        exit(f"Failed to Insert Changelist(name={failure_cl.list_key.changelist_name}) for unknown reason (neither key nor id conflict has occurred).")
