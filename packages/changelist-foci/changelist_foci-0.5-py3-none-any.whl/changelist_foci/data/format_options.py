""" The Options for FOCI Formatting.

**Fields:**
 - full_path (bool): Whether to display the full path to the file. Default: False.
 - no_file_ext (bool): Whether to filter file extensions (except move with different extensions). Default: False.
 - file_name (bool): Whether to display the file name. Removes any parent directories. Default: False.
 - markdown (bool): Whether to use Markdown in FOCI. Default: False.
"""
from collections import namedtuple


FormatOptions = namedtuple(
    typename='FormatOptions',
    field_names=(
        'full_path',
        'no_file_ext',
        'file_name',
        'markdown',
    ),
    defaults=(
        False, False, False, False,
    ),
)
