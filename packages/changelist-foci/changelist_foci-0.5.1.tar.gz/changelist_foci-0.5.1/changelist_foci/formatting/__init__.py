""" Formatting Package.
 - Manage division between original FOCI and Markdown.
"""
from typing import Callable

from changelist_data.changelist import Changelist

from changelist_foci.data.format_options import FormatOptions


def get_changelist_formatter(
    format_options: FormatOptions,
) -> Callable[[Changelist], str]:
    """ Obtain a function that formats Changelist FOCI.

**Parameters:**
 - format_options (FormatOptions): The Formatting Options for File paths.

**Returns:**
 Callable[[Changelist], str] - A Function returning FOCI for given Changelist.
    """
    if format_options.markdown:
        raise NotImplementedError("Markdown is not implemented yet.")
    # Original Changelist FOCI.
    from changelist_foci.formatting.foci_formatter import format_changelist
    return lambda cl: format_changelist(cl, format_options)
