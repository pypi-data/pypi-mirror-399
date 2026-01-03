""" NamedTuple containing Fields describing a File Change.
 - This data container builds on the common FileChange tuple, adding key sorting components.

**ChangeData NamedTuple Fields:**
 - file_change (FileChange): The NamedTuple containing the original FileChange properties. These are not used during sort.
 - sort_path (str?): The Path to use for sorting.
 - first_dir (str?): The First Directory in the file sort path.
 - file_basename (str?): The basename of the file sort path.
 - file_ext (str?): The File Extension.
"""
from collections import namedtuple
from os.path import basename

from changelist_data.file_change import FileChange


ChangeData = namedtuple(
    'ChangeData',
    (
        'file_change',
        'sort_path',
        'first_dir',
        'file_basename',
        'file_ext',
     ),
)


def _get_sort_path(fc: FileChange) -> str | None:
    """ Determine the Path to use for sorting.
 - Prefer AfterPath.
    """
    return fc.after_path if fc.after_path is not None else fc.before_path


def _get_first_dir(sort_path: str) -> str | None:
    """ Obtain the First Directory in the file sort path, or None.
    """
    start_idx = 1 if sort_path.startswith('/') else 0
    try:
        end_idx = sort_path.index('/', start_idx)
        return sort_path[start_idx:end_idx]
    except ValueError:
        return None


def _get_file_ext(file_basename: str) -> str | None:
    """ Obtain the File Extension from the basename, or return None.
    """
    try:
        return file_basename[file_basename.index('.', 1) + 1:]
    except ValueError:
        return None


def expand_fc(fc: FileChange) -> ChangeData:
    if (sort_path := _get_sort_path(fc)) is None:
        raise ValueError
    file_basename = basename(sort_path)
    return ChangeData(
        file_change=fc,
        sort_path=sort_path,
        first_dir=_get_first_dir(sort_path),
        file_basename=file_basename,
        file_ext=_get_file_ext(file_basename),
    )
