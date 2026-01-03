""" String formatting operations for file paths.
"""
from os.path import splitext, basename
from typing import Callable

from changelist_foci.data.format_options import FormatOptions


def get_path_formatter(
    options: FormatOptions,
) -> Callable[[str], str]:
    """ Get a Function that will format the path strings.

**Parameters:**
 - options (FormatOptions): The options specifying the target path format.

**Returns:**
 Callable[[str], str] - A Function that reduces a path string to the selected segments for optimal presentation.
    """
    if options.full_path:
        if options.no_file_ext: # Filter FileExt
            return lambda x: splitext(x)[0]
        return lambda x: x
    if options.file_name:
        if options.no_file_ext: # Filter FileExt
            return lambda x: splitext(basename(x))[0]
        return lambda x: basename(x)
    if options.no_file_ext: # Filter FileExt
        return lambda x: splitext(x.lstrip('/'))[0]
    return lambda x: x.lstrip('/')
