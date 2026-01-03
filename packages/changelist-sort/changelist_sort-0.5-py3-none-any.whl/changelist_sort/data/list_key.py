""" List Keys Definitions.

**ListKey NamedTuple Fields:**
 - key (str): The key used to quickly search for the changelist.
 - changelist_name (str): The full user defined name for the changelist.
"""
from collections import namedtuple

from changelist_data import changelist


ListKey = namedtuple(
    'ListKey',
    ('key', 'changelist_name',)
)


def compute_key(cl_name: str) -> ListKey:
    """ Compute a Key to use for a given Changelist Name.
 - computation is a sequence of reduction operations

**Parameters:**
 - cl_name (str): The Changelist Name to be included in the ListKey.

**Returns:**
 ListKey - A ListKey instance containing the Key and Changelist Name.
    """
    return ListKey(
        key=changelist.compute_key(cl_name),
        changelist_name=cl_name
    )
