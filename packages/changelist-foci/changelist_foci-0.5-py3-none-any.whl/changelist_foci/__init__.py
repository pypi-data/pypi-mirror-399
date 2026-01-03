""" CL-FOCI Package Methods.
 Author: DK96-OS 2024 - 2025
"""
from changelist_foci.data import update_cl_comments, get_changelist_selector, update_data_storage
from changelist_foci.data.input_data import InputData
from changelist_foci.formatting import get_changelist_formatter


_CHANGELIST_NOT_FOUND_ERROR_MSG = "Changelist not Found: "


def get_changelist_foci(
    input_data: InputData,
) -> str:
    """ Processes InputData, returning the FOCI string.
 - Ignores ChangelistDataStorage and Comment Feature.

**Parameters:**
 - input_data (InputData): The program input data.

**Returns:**
 str - The FOCI formatted output.
    """
    foci_formatter = get_changelist_formatter(input_data.format_options)
    if (cl_selector := get_changelist_selector(input_data.changelist_name)) is not None:
        if len(selected_lists := list(filter(cl_selector, input_data.changelists))) < 1:
            exit(_CHANGELIST_NOT_FOUND_ERROR_MSG + str(input_data.changelist_name))
        return '\n\n'.join(foci_formatter(cl) for cl in selected_lists)
    return '\n\n'.join(
        foci_formatter(cl) for cl in filter(
            lambda x: len(x.changes) > 0,
            input_data.changelists
        )
    )


def process_cl_foci(
    input_data: InputData,
) -> str:
    """ Returns a String for printing, or None if writing to Storage.
 - The Comments option enables writing FOCI to Changelists in Storage.

**Parameters:**
 - input_data (InputData): The program Inputs.

**Returns:**
 str - The processed FOCI string, or empty if storage was updated.
    """
    if input_data.changelist_data_storage is None:
        return get_changelist_foci(input_data)
    update_data_storage(
        input_data.changelist_data_storage,
        list(update_cl_comments(
            input_data.changelists,
            get_changelist_formatter(input_data.format_options),
            get_changelist_selector(input_data.changelist_name),
        ))
    )
    return '' # Otherwise the method returns None
