""" The Input Package level methods.
"""
from changelist_data import load_storage_from_file_arguments

from changelist_foci.data.format_options import FormatOptions
from changelist_foci.data.input_data import InputData
from changelist_foci.input.argument_parser import parse_arguments, ArgumentData


def validate_input(
    arguments: list[str],
) -> InputData:
    """ Given the Command Line Arguments, build the program InputData.
 - Parse arguments with argument parser.
 - Load Storage using Arguments or search Default locations.

**Parameters:**
 - arguments (list[str]): The Command Line Arguments received by the program.

**Returns:**
 InputData - The formatted InputData.
    """
    arg_data: ArgumentData = parse_arguments(arguments)
    cl_data_storage = load_storage_from_file_arguments(
        changelists_file=arg_data.changelists_path,
        workspace_file=arg_data.workspace_path,
    )
    return InputData(
        changelists=cl_data_storage.generate_changelists(),
        changelist_name=arg_data.changelist_name,
        format_options=_get_format_options(arg_data),
        changelist_data_storage=cl_data_storage if arg_data.comment else None,
    )


def _get_format_options(
    arg_data: ArgumentData,
) -> FormatOptions:
    return FormatOptions(
        full_path=arg_data.full_path,
        no_file_ext=arg_data.no_file_ext,
        file_name=arg_data.filename,
        markdown=arg_data.markdown,
    )
