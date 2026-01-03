""" Valid Input Data Class.
"""
from dataclasses import dataclass
from typing import Iterable

from changelist_data.changelist import Changelist
from changelist_data.storage.changelist_data_storage import ChangelistDataStorage

from changelist_foci.data.format_options import FormatOptions


@dataclass(frozen=True)
class InputData:
    """ A Data Class Containing Program Input.

**Fields:**
 - changelists (Iterable[Changelist]): The Iterable of changelists to process.
 - changelist_name (str?): The name or prefix of Changelists to select, or None.
 - format_options (FormatOptions): The options for output formatting.
 - changelist_data_storage (ChangelistDataStorage?): If this field is present, insert FOCI into Changelist Comments instead of printing.
    """
    changelists: Iterable[Changelist]
    changelist_name: str | None
    format_options: FormatOptions
    changelist_data_storage: ChangelistDataStorage | None = None
