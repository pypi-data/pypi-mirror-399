from enum import StrEnum, auto


class Revision(StrEnum):
    v2018 = "2018"
    UNKNOWN = auto()


# String value matches the directory name under assets
class FormName(StrEnum):
    PS1 = "PS-1"
    PS2 = "PS-2"
    PS3 = "PS-3"
    PS4 = "PS-4"
    PS5 = "PS-5"
    UNKNOWN = auto()


# Start with a constant for now, can revise later
# when other forms/bounding boxes are available.
PS4_SAMPLING_DATA = "sample-data.npy"
PS4_COLUMN_TOTALS = "column-totals.npy"
PS4_PAGE_TOTALS = "page-totals.npy"
PS4_SAMPLING_PATTERNS = "sampling-patterns.npy"
