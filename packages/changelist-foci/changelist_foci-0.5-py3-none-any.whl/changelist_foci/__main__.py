#!/usr/bin/python


def main():
    from sys import argv
    # Validate Input Data
    from changelist_foci.input import validate_input
    input_data = validate_input(argv[1:])
    # Run CL-FOCI Process
    from changelist_foci import process_cl_foci
    print(process_cl_foci(input_data))


if __name__ == "__main__":
    from pathlib import Path
    from sys import path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    current_directory = Path(__file__).resolve().parent.parent
    path.append(str(current_directory)) # Add the directory to sys.path
    # Now imports have parent dir in path
    main()
