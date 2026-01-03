""" Defines and Validates Argument Syntax.
 - Encapsulates Argument Parser.
 - Returns Argument Data, the args provided by the User in a NamedTuple object.
"""
from argparse import ArgumentParser
from collections import namedtuple
from sys import exit
from xml.etree.ElementTree import ParseError

from changelist_data import validate_string_argument


ArgumentData = namedtuple(
    'ArgumentData',
    (
        'changelists_path',
        'workspace_path',
        'sourceset_sort',
        'remove_empty',
        'sort_xml_path',
        'generate_sort_xml',
        'enable_workspace_overwrite',
    ),
    defaults=(
        None, None, False, False, None, False, False,
    ),
)


def parse_arguments(
    arguments: list[str] | None,
) -> ArgumentData:
    """ Parse command line arguments.

**Parameters:**
 - args: A list of argument strings.

**Returns:**
 ArgumentData - NamedTuple data container for valid arguments.

**ArgumentData NamedTuple:*
 - changelists_path (str?): The path to the Changelists file, or None to enable defaults. Default: None.
 - workspace_path (str?): The path to the workspace file, or None to enable defaults. Default: None
 - remove_empty (bool): Flag indicating that empty changelists should be removed. Default: False.
 - sort_xml_path (str?): The string path to the sort XML file, if not in default location. Default: None.
 - sourceset_sort (bool): Flag for the SourceSet SortMode. Default: False.
 - generate_sort_xml (bool): Generate the config.xml file for the project. Default: False.
 - enable_workspace_overwrite (bool): Allow the Workspace file to be overwritten. Default: False.
    """
    if arguments is None or (number_of_args := len(arguments)) == 0:
        return ArgumentData()
    elif number_of_args > 6:
        exit('Too many arguments')
    try: # Initialize the Parser and Parse Immediately
        return _validate_arguments(_define_arguments().parse_args(arguments))
    except ParseError:
        exit("Unable to Parse Arguments.")


def _validate_arguments(
    parsed_args,
) -> ArgumentData:
    """ Checks the values received from the ArgParser.
        - Uses Validate Name method from StringValidation.

    Parameters:
    - parsed_args : The object returned by ArgumentParser.

    Returns:
    ArgumentData - A DataClass of syntactically correct arguments.
    """
    if (cl_file := parsed_args.changelists_file) is not None:
        if not validate_string_argument(cl_file):
            exit("Invalid Changelists File Name")
    if (ws_file := parsed_args.workspace_file) is not None:
        if not validate_string_argument(ws_file):
            exit("Invalid Workspace File Name")
    return ArgumentData(
        changelists_path=cl_file,
        workspace_path=ws_file,
        sourceset_sort=parsed_args.sourceset_sort,
        remove_empty=parsed_args.remove_empty,
        sort_xml_path=parsed_args.sort_xml_file,
        generate_sort_xml=parsed_args.generate_sort_xml,
        enable_workspace_overwrite=parsed_args.enable_workspace_overwrite,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
        - Sets Required/Optional Arguments and Flags.

    Returns:
    argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description='Sorts file changes into managed changelists using the sort.xml config file.',
    )
    # Introduced in Version 3.14: Color, SuggestOnError.
    parser.color = True
    parser.suggest_on_error = True
    # Optional Arguments
    parser.add_argument(
        '--changelists_file', '--data_file',
        type=str,
        default=None,
        help='The Changelists Data File. Searches default location if not provided.'
    )
    parser.add_argument(
        '--workspace_file',
        type=str,
        default=None,
        help='The Workspace File containing the ChangeList data. Searches default location if not provided.'
    )
    parser.add_argument(
        '--enable_workspace_overwrite', '-w',
        action='store_true',
        default=False,
        help='Enable overwriting the local Workspace file.'
    )
    parser.add_argument(
        '--sourceset_sort', '--sourceset-sort', '-s',
        action='store_true',
        default=False,
        help='A Flag indicating that SourceSet Sort is to be used primarily. Fallback to Module Sort.',
    )
    parser.add_argument(
        '--remove_empty', '--remove-empty', '-r',
        action='store_true',
        default=False,
        help='A Flag indicating that empty changelists are to be removed after sorting.',
    )
    parser.add_argument(
        '--sort_xml_file',
        type=str,
        default=None,
        help='The path to the Sort XML file, if not in a default location.'
    )
    parser.add_argument(
        '--generate_sort_xml',
        action='store_true',
        default=False,
        help='Generate the .changelist/sort.xml file for the project.',
    )
    return parser
