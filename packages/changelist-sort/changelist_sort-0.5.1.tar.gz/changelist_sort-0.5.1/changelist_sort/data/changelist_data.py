""" The Data Container for a ChangeList.

**ChangelistData NamedTuple Fields:**
 - id (str): The unique id of the changelist.
 - list_key (ListKey): The key-ChangelistName pair, used while sorting.
 - changes (list[ChangeData]): The list of file changes in the changelist.
 - comment (str): The comment associated with the changelist. Default: Empty str.
 - is_default (bool): Whether this is the active changelist. Default: False.
"""
from collections import namedtuple

from changelist_data.changelist import Changelist

from changelist_sort.data.change_data import expand_fc
from changelist_sort.data.list_key import compute_key


ChangelistData = namedtuple(
    'ChangelistData',
    (
        'id',
        'list_key',
        'changes',
        'comment',
        'is_default',
    ),
    defaults=(
        '', False,
    )
)


def expand_cl(
    changelist: Changelist,
) -> ChangelistData:
    """ Expand the common Changelist namedtuple container with additional sorting fields.

**Parameters:**
 - changelist (Changelist): The common changelist data.

**Returns:**
 ChangelistData - The expanded ChangelistData NamedTuple.
    """
    return ChangelistData(
        id=changelist.id,
        list_key=compute_key(changelist.name),
        changes=[ expand_fc(fc) for fc in changelist.changes ],
        comment=changelist.comment,
        is_default=changelist.is_default,
    )
