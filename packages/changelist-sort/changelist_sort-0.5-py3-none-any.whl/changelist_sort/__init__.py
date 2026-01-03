""" CL-SORT Main Package Methods.
 Author: DK96-OS 2024 - 2025
"""
from typing import Iterable, Generator

from changelist_data.changelist import Changelist
from changelist_data.storage.changelist_data_storage import ChangelistDataStorage
from changelist_data.storage.storage_type import StorageType

from changelist_sort.input import InputData
from changelist_sort.sorting import sort, SortingChangelist, sort_with_mode, SortMode


def process_cl_sort(
    input_data: InputData,
) -> str | None:
    """ Process the ChangelistSort InputData.

**Parameters:**
 - input_data (InputData): The Cl-Sort Input Data.

**Returns:**
 str? - A printable output, if applicable for the program input. Normally None.
    """
    if input_data.generate_sort_xml:
        return _generate_sort_config()
    if input_data.storage.storage_type == StorageType.WORKSPACE:
        if not input_data.enable_workspace_overwrite:
            exit('Workspace Overwrite Protection is enabled. Use -w to disable.')
    sort_changelist_storage(
        input_data.storage,
        input_data.sort_mode,
        input_data.remove_empty,
        input_data.sorting_config,
    )


def generate_sorted_changelists(
    initial_changelists: Iterable[Changelist],
    sort_mode: SortMode = SortMode.MODULE,
    remove_empty: bool = False,
    sorting_config: list[SortingChangelist] | None = None,
) -> Generator[Changelist, None, None]:
    """ Sort the Changelists and yield them through a generator.

**Parameters:**
 - initial_changelists (Iterable[Changelist]): The Source Changelist information.
 - sort_mode (SortMode): The soring mode to use in absence of SortingConfig. Default: Module.
 - remove_empty (bool): Whether to filter empty changelists from the generated output. Default: False.
 - sorting_config (list[SortingChangelist]?): An optional list of Sorting Changelist Patterns. Default: None.

**Yields:**
 Changelist - The sorted Changelists data tuples.
    """
    if sorting_config is None:
         yield from sort_with_mode(
            initial_list=initial_changelists,
            mode=sort_mode,
            filter_empty=remove_empty,
        )
    else:
        yield from sort(
            initial_list=initial_changelists,
            sorting_config=sorting_config,
            filter_empty=remove_empty,
        )


def sort_changelist_storage(
    storage: ChangelistDataStorage,
    sort_mode: SortMode = SortMode.MODULE,
    remove_empty: bool = False,
    sorting_config: list[SortingChangelist] | None = None,
):
    """ Generate Changelists from Storage object, Sort them, and update Storage object (in-memory).

**Parameters:**
 - storage (ChangelistDataStorage): The Storage object with read and write access to changelists data.
 - sort_mode (SortMode): The Sorting Mode to apply during operation. Overridden by sorting_config parameter. Default: Module.
 - remove_empty (bool): Whether to remove empty Changelists, before writing to storage. Default: False.
 - sorting_config (list[SortingChangelist]?): The changelist sorting criteria. Default: None.
    """
    storage.update_changelists(
        list(generate_sorted_changelists(
            storage.generate_changelists(),
            sort_mode,
            remove_empty,
            sorting_config,
        ))
    )
    try:
        storage.write_to_storage()
    except PermissionError:
        exit('Failed to write CL-Sort storage file due to permissions.')
    except OSError as e:
        exit(f'A (temporary) error has occurred while writing CL-Sort storage file: {e}')


def _generate_sort_config():
    from changelist_sort.xml.generator import generate_sort_xml
    if generate_sort_xml(None):
        return "Sort file created: .changelists/sort.xml"
    exit("Failed to create sort.xml file.")
