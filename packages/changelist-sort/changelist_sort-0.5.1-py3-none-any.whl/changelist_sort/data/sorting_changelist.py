""" Developer Changelist Settings and Methods
"""
from dataclasses import dataclass

from changelist_sort.data.change_data import ChangeData
from changelist_sort.data.list_key import ListKey
from changelist_sort.data.sorting_file_pattern import SortingFilePattern
from changelist_sort.sorting.module_type import ModuleType


@dataclass(frozen=True)
class SortingChangelist:
    """ A Changelist data class designed for sorting.

**Fields:**
 - list_key (ListKey): The Key and Name of the Changelist.
 - file_patterns (list[SortingFilePattern]): The FilePatterns
 - module_type (ModuleType?): The Type of Module to match Files with. None allows files from any module.
    """
    list_key: ListKey
    file_patterns: list[SortingFilePattern]
    module_type: ModuleType | None = None

    def check_file(self, file: ChangeData) -> bool:
        """ Determine if the File can be added to this Changelist.
 - If the FilePatterns are empty, always returns False.

**Parameters:**
 - file (ChangeData): The ChangeData of the File to pattern match.

**Returns:**
 bool - True if the File matches all patterns in this Changelist.
        """
        if len(self.file_patterns) == 0:
            return False
        for fp in self.file_patterns:
            if not fp.check_file(file):
                return False
        return True
