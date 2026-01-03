""" The Data Package Methods translating between changelist_data and changelist_sort data objects.
 - expand_cl_iterable: Calculates sorting information and creates changelist_sort data objects.
 - compact_cl_iterable: Discard sorting information, keeping the base changelist_data fields for storage.
"""
from typing import Iterable, Generator

from changelist_data.changelist import Changelist

from changelist_sort.data.changelist_data import ChangelistData, expand_cl


def expand_cl_iterable(
    iterable: Iterable[Changelist],
) -> Generator[ChangelistData, None, None]:
    """ Convert a base changelist_data into a changelist_sort Changelist data type.
 - Calculates key sorting values from the base data, saves them in a new data type.
 - The inner FileChange list is also expanded into a list of changelist_sort data type.

**Parameters:**
 - iterable (Changelist): An input collection of changelist_data Changelists.

**Yields:**
 ChangelistData - Expanded data type, created from the base data.
    """
    for cl in iterable:
        yield expand_cl(cl)


def compact_cl_iterable(
    iterable: Iterable[ChangelistData],
) -> Generator[Changelist, None, None]:
    """ Reverse the changelist_sort expansion, re-acquiring the base changelist_data types.

**Parameters:**
 - iterable (ChangelistData): The expanded Changelists to reduce to the base data type.

**Yields:**
 Changelist - The changelist_data package data type.
    """
    for cl_data in iterable:
        yield Changelist(
            id=cl_data.id,
            name=cl_data.list_key.changelist_name,
            changes=[cd.file_change for cd in cl_data.changes],
            comment=cl_data.comment,
            is_default=cl_data.is_default,
        )
