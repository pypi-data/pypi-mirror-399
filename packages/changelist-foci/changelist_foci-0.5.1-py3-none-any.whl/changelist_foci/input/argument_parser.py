""" Defines and Validates Argument Syntax.
 - Encapsulates Argument Parser.
 - Syntax Validation:
   - The changelist name, if exists is checked for valid characters.
   - The workspace path, if exists is currently unvalidated.
 - Returns Argument Data tuple, the args provided by the User.
"""
from argparse import ArgumentParser
from collections import namedtuple
from sys import exit

from changelist_data.validation.arguments import validate_string_argument


ArgumentData = namedtuple(
    'ArgumentData',
    field_names=(
        # Input Data File Options
        'changelists_path', 'workspace_path',
        # CL Name Prefix Selector
        'changelist_name',
        # Format Options
        'full_path', 'no_file_ext', 'filename', 'markdown',
        # Write to Storage comments
        'comment',
    ),
    defaults=(
        None, None, None, False, False, False, False, False,
    ),
)


def parse_arguments(args: list[str] | None = None) -> ArgumentData:
    """ Parse command line arguments.
 - Returns Default Argument Data when input is empty.

**Parameters:**
 - args (list[str]?): A list of argument strings.

**Returns:**
 ArgumentData - A NamedTuple for syntactically valid Argument data.

**ArgumentData NamedTuple:**
 - changelists_path (str?): The path to the Changelists data xml file, or none to check default paths.
 - workspace_path (str?): The path to the Workspace xml file, or none to check default paths.
 - changelist_name (str?): The name of the changelist, or None to use the Active Changelist.
 - full_path (bool): Display the Full File Path.
 - no_file_ext (bool): Remove the File Extension.
 - filename (bool): Remove the Parent Directories.
 - markdown (bool): Whether to use Markdown formatting.
 - comment (bool): Whether to insert FOCI into the Changelist Comments, rather than printing.
    """
    if args is None:
        return ArgumentData()
    # Initialize the Parser and Parse Immediately
    try:
        parsed_args = _define_arguments().parse_args(args)
    except SystemExit:
        exit("Unable to Parse Arguments.")
    return _validate_arguments(parsed_args)


def _validate_arguments(
    parsed_args,
) -> ArgumentData:
    """ Checks the values received from the ArgParser.
 - Uses Validate Name method from StringValidation.

**Parameters:**
 - parsed_args : The object returned by ArgumentParser.

**Returns:**
 ArgumentData - A DataClass of syntactically correct arguments.
    """
    # Validate Changelist Name
    if (changelist := parsed_args.cl_name) is not None:
        if not validate_string_argument(changelist):
            exit("The ChangeList Name was invalid.")
    # Check Changelist Path Argument
    if (cl_path := parsed_args.changelists_file) is not None:
        if not validate_string_argument(cl_path):
            exit("changelists_file argument invalid.")
    # Check Workspace Argument
    if (ws_path := parsed_args.workspace_file) is not None:
        if not validate_string_argument(ws_path):
            exit("workspace_path argument invalid.")
    #
    return ArgumentData(
        changelists_path=cl_path,
        workspace_path=ws_path,
        changelist_name=changelist,
        full_path=parsed_args.full_path,
        no_file_ext=parsed_args.no_file_ext,
        filename=parsed_args.filename,
        markdown=parsed_args.markdown,
        comment=parsed_args.comment,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
 - Sets Required/Optional Arguments and Flags.

**Returns:**
 argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description='Generates ChangeList FOCI (File Oriented Commit Information) from Changelist Data',
    )
    # Introduced in Version 3.14: Color, SuggestOnError.
    parser.color = True
    parser.suggest_on_error = True
    # Optional Arguments
    parser.add_argument(
        '--changelists_file',
        type=str,
        default=None,
        help='The Path to the Changelists file. Searches default path if not given.',
    )
    parser.add_argument(
        '--workspace_file',
        type=str,
        default=None,
        help='The Path to the workspace file. Searches default path if not given.',
    )
    parser.add_argument(
        '--cl_name',
        type=str,
        default=None,
        help='Select Changelists by Name Prefix. Allows multiple Changelists to be selected. Matching is not case-sensitive.'
    )
    parser.add_argument(
        '--full_path',
        action='store_true',
        default=False,
        help='Display the Full File Path.',
    )
    parser.add_argument(
        '--no_file_ext', '-x',
        action='store_true',
        default=False,
        help='Remove File Extension from File paths.',
    )
    parser.add_argument(
        '--filename', '-f',
        action='store_true',
        default=False,
        help='Remove Parent Directories from File paths.',
    )
    parser.add_argument(
        '--markdown', '-m',
        action='store_true',
        default=False,
        help='Format FOCI in Markdown.',
    )
    parser.add_argument(
        '--comment', '-c',
        action='store_true',
        default=False,
        help='Insert FOCI into Changelist Workspace Comments instead of printing.',
    )
    return parser
