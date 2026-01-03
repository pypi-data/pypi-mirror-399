""" Categorize Types of Modules at a high level to make sorting definitions easier to write.
"""
from enum import Enum


class ModuleType(Enum):
    """ Categorization by type of Module.
 - Used in Module Sort and beyond. Every proper file path is one of these types.
 - Sorting Changelists should target a specific type of module.
    """
    MODULE = 'module'
    ROOT = 'root'
    GRADLE = 'gradle'
    HIDDEN = 'hidden'


def determine_module_type(
    module_type: str | None,
) -> ModuleType | None:
    """ Determine the ModuleType, or return None.

**Parameters:**
 - module_type (str?): The module type input string.

**Returns:*
 ModuleType? - The matching ModuleType enum, or None.
    """
    if not isinstance(module_type, str):
        return None
    elif (m := module_type.lower()) == 'module':
        return ModuleType.MODULE
    elif m == 'root':
        return ModuleType.ROOT
    elif m == 'gradle':
        return ModuleType.GRADLE
    elif m == 'hidden':
        return ModuleType.HIDDEN
    else:
        return None
