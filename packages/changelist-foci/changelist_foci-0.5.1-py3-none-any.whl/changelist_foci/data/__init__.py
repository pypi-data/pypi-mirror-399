""" Data Classes and Related Methods.
"""
from typing import Iterable, Callable, Generator

from changelist_data import ChangelistDataStorage
from changelist_data.changelist import Changelist


def get_changelist_selector(
    cl_name_prefix: str | None,
) -> Callable[[Changelist], bool] | None:
    """ Obtain a Function that selects Changelists by their name property.
 - Compares lowercased strings. Both the changelist_name argument, and each Changelist name is lowercased.

**Parameters:**
 - cl_name_prefix (str?): The prefix/name to select in the collection of Changelists.

**Returns:**
 Callable[[Changelist], bool]? - The selector callable, or None for all Changelists.
    """
    if cl_name_prefix is None:
        return None
    lowered_prefix = cl_name_prefix.lower()
    return lambda cl: cl.name.lower().startswith(lowered_prefix)


def update_cl_comments(
    changelists: Iterable[Changelist],
    cl_formatter: Callable[[Changelist], str],
    cl_selector: Callable[[Changelist], bool] | None = None,
) -> Generator[Changelist, None, None]:
    """ Update Changelist Comment Fields with Freshly Formatted FOCI.
 - Provides option to select Changelists to update with a selector function.
 - By default, updates all Changelists in the source Iterable.

**Parameters:**
 - changelists (Iterable[Changelist]): The Changelists to be processed, and potentially updated.
 - cl_formatter (Callable[[Changelist], str]): Formats a Changelist object into FOCI string.
 - cl_selector (Callable[[Changelist], bool]?): Selects the Changelist(s) to update. If None, updates all Changelists.

**Yields:**
 Changelist - The updated Changelist objects, some of which may have changed, depending on InputData options.
    """
    if cl_selector is None: # Update All
        for cl in changelists:
            yield Changelist(
                id=cl.id,
                name=cl.name,
                changes=cl.changes,
                comment=cl_formatter(cl),
                is_default=cl.is_default,
            )
    else: # Only update selected changelists.
        for cl in changelists:
            yield Changelist(
                id=cl.id,
                name=cl.name,
                changes=cl.changes,
                comment=cl_formatter(cl),
                is_default=cl.is_default,
            ) if cl_selector(cl) else cl # Avoids reconstructing un-changed objects.


def update_data_storage(
    cl_data_storage: ChangelistDataStorage,
    updated_changelists: list[Changelist],
):
    """ Update the Data Storage with a new list of Changelist Data.

**Parameters:**
 - cl_data_storage (ChangelistDataStorage): The ChangelistData Storage object.
 - updated_changelists (list[Changelist]): The new Changelist Data list to overwrite the existing data in storage.

**Raises:**
 PermissionError - when the Storage file cannot be written to, due to permissions.
 OSError - A file system error during file write, may be a temporary issue.
    """
    cl_data_storage.update_changelists(updated_changelists)
    try:
        cl_data_storage.write_to_storage()
    except PermissionError:
        exit('Changelist Storage file write failed due to Permissions.')
    except OSError as e:
        exit(f'Changelist Storage write operation failed: {e}')
