# Changelist-FOCI
Format file change information from your changelists in FOCI (File-Oriented Commit Information).
- Potential support for more formats (markdown coming soon).

### Requirements
- Python 3.10 or higher.
- pip (or similar package manager).
- cli or bash capabilities.

## Usage Scenarios
This package provides text formatting and re-direction via 2 methods:
1. Print Formatted Text to Output.
    - Default mode of operation.
2. Insert Formatted Text into Data Storage.
    - Add `-c` or `--comment` argument.
    - Useful with Workspace File workflows, where the Comment fields are loaded into commit messages.

## How It Works
1. Uses changelist_data to read/load Changelist data objects.
2. Changelists are filtered and file names are formatted in FOCI (File Oriented Commit Information).
3. FOCI information is directed toward standard output or storage.

## CLI Arguments
### Changelist Selection
**Changelist Name:** `--cl_name`
An optional argument, that selects Changelists by the start of their names.

If changelist name argument is not provided, all non-empty changelists will be formatted.

### Workspace Comments Feature
**FOCI Comments:** `-c` or `--comment`
Insert the FOCI into the Data file comments, rather than printing.
- Compatible with Changelist Selection Feature.
- Works with both Workspace and Changelist data files.

### Data File Selection
**Changelists File Path:** `--changelists_file`
An optional argument used to select a Changelist data file not in the default location.

**Workspace File Path:** `--workspace_file`
An optional argument, used to select a workspace file not in the default location.

If neither file path argument is provided, changelist_data package will look in the default locations, starting with the Changelist data file.

### FOCI Subjects (File Path) Formatting
**Full Path:** `--full_path`
The full path of the file is given in Line Subjects.
 - Includes the first slash of directories in the project root (removed by default). 

**File Extension:** `--no_file_ext` or `-x`
Remove the File Extension from File Names.

**File Name:** `--filename` or `-f`
Include only the File Name in Subject Lines.
 - Removes the whole path to the File.
 - May be combined with the File Extension flag. 

**Markdown:** `--markdown` or `-m`
Alter original FOCI format with Markdown.
 - To be implemented in 0.5.x

## Package Structure
- `changelist_foci/`
- `changelist_foci/data/`
- `changelist_foci/formatting/`
- `changelist_foci/input/`
