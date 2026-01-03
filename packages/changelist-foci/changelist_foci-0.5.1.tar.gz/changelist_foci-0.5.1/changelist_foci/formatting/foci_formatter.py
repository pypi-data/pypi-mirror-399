""" Methods formatting in the original Changelist FOCI format.
"""
from typing import Callable

from changelist_data.changelist import Changelist
from changelist_data.file_change import FileChange

from changelist_foci.data.format_options import FormatOptions
from changelist_foci.formatting.path_formatter import get_path_formatter


def format_changelist(
    changelist: Changelist,
    format_options: FormatOptions,
) -> str:
    """ Obtain the FOCI of a Changelist.

**Parameters:**
 - changelist (Changelist): The Changelist to process and format.
 - format_options (FormatOptions): The formatting options for file paths in FOCI subjects.

**Returns:**
 str - The FOCI string.
    """
    foci_header = f"{changelist.name}:\n" if len(changelist.name) > 0 else ''
    # Use this formatter method on Changelist file paths.
    path_formatter = get_path_formatter(format_options)
    return foci_header + "\n".join(
        sorted(
            format_subject(file_change, path_formatter)
            for file_change in changelist.changes
        )
    )


def format_subject(
    file_change: FileChange,
    path_formatter: Callable[[str], str],
) -> str:
    """ Obtain the FOCI-formatted Subject for the given FileChange.

**Parameters:**
 - file_change (FileChange): The data container for the file paths.
 - path_formatter (Callable): The method used to format file paths. See path_formatter module.

**Returns:**
 str - The FOCI-Formatted Subject line.
    """
    return _get_foci_subject(
        _format_file_paths(
            file_change,
            path_formatter
        )
    )


def _format_file_paths(
    fc: FileChange,
    formatter: Callable[[str], str],
) -> tuple[str | None, str | None]:
    return (
        formatter(fc.before_path) if fc.before_path is not None else None,
        formatter(fc.after_path) if fc.after_path is not None else None,
    )


def _get_foci_subject(
    formatted_paths: tuple[str | None, str | None],
) -> str:
    if (before := formatted_paths[0]) is None:
        if formatted_paths[1] is None:
            return ''
        # Only the After Path exists
        return f"* Create {formatted_paths[1]}"
    if (after := formatted_paths[1]) is None:
        return f"* Remove {before}"
    # Compare Both Full Paths
    if before == after:
        return f"* Update {before}"
    # Different Before and After Paths
    return f"* Move {before} to {after}"
