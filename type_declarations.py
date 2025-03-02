from typing import TypedDict, NotRequired
from enum import Enum

# A JsonCustomField is a user definable name-value pair.
# The contents do not effect checklist behavior but are visible on the LRU.
# Set name and value to an empty string ("") if no custom field is desired.
class JsonCustomField(TypedDict):
    name: str  # up to 9 characters long.
    value: str  # up to 255 characters long. Must be an empty string if name is an empty string.

# A JsonChecklistRef is an index into the file's groups and into that group's checklists.
class JsonChecklistRef(TypedDict):
    group: int  # index into file.groups
    checklist: int  # index into group.checklists

# A JsonEntry is an item within a checklist.
# An entry can be colored, sized, formatted and more.
# Many of the options on a JsonEntry only apply for certain types of entries.
class JsonEntry(TypedDict):
    text: str
    response: NotRequired[str]  # only relevant if type interaction is checkbox
    type: str  # name of entry type or "Link" or "Branch"

    blanksBelow: NotRequired[int]  # 0 through 10; defaults to 0
    justification: NotRequired[str]  # left, center, indent1, indent2, indent3, or indent4; defaults to left
    image: NotRequired[str]  # name of image

    linkedChecklist: NotRequired[JsonChecklistRef]  # only relevant if type is "Link"
    linkedSynopticPage: NotRequired[str]  # only relevant if type is "Link" and linkedChecklist isn't set
    branches: NotRequired[list[int]]  # only relevant if type is "Branch"; indexes into file.branchChecklists
    hideParentCheckbox: NotRequired[bool]  # only relevant if type is "Branch". Cannot hide checkbox if only one branch is set.

    fallbackText: NotRequired[str]  # only relevant if linkedSynopticPage is set

# A JsonCasAlert identifies a CAS Alert and some of its leaves.
# leafMask is NOT SUPPORTED until CheckSet version 1.11.0
class JsonCasAlert(TypedDict):
    class_: str  # ALRT_CLASS_ARFRM, ALRT_CLASS_OEM, etc.
    name: str
    leafMask: NotRequired[int]  # bitmask of leaves to trigger on; 0 to 65535; defaults to 65535

# A JsonChecklist is a sequence of entries.
# Multiple CAS alerts can be linked to trigger this checklist when the alert is active.
class JsonChecklist(TypedDict):
    name: str
    entries: list[JsonEntry]
    linkedAlerts: NotRequired[list[JsonCasAlert]]

# A JsonGroup is a named collection of checklists.
class JsonGroup(TypedDict):
    name: str  # up to 127 characters long
    checklists: list[JsonChecklist]

# A JsonEntryType is a format and interaction style.
# It is specified at the file level, usable by multiple entries, and referenced by name.
class JsonEntryType(TypedDict):
    name: str  # must be unique and not "Link" or "Branch"

    color: str  # cyan, gray, green, lime, magenta, maroon, navy, olive, red, silver, white, yellow
    fontSize: int  # 7 to 25 except 11, 19, 21, 22, and 24
    interaction: str  # checkbox, scrollStop, or noScrollStop

# A JsonImage is a text encoded image.
# It is specified at the file level, usable by multiple entries, and referenced by name.
class JsonImage(TypedDict):
    name: str  # must be unique
    format: str  # bmp, jpeg, or png
    data: str  # base64 encoding of the bytes

# The JsonFile structure should be the .JSON file's root object.
class JsonFile(TypedDict):
    version: str  # the format version; should be set to "1" if using this format
    description: str
    customFields: list[JsonCustomField]  # exactly 5 custom fields must be specified.

    groups: list[JsonGroup]
    branchChecklists: list[JsonChecklist]
    entryTypes: list[JsonEntryType]
    images: list

    a661synoptics: NotRequired[list]
    legacySpaceEncoding: NotRequired[bool]
    defaultChecklist: NotRequired[JsonChecklistRef]

# The MSFS Avionics Framework supported item types.
class ItemType(Enum):
    Actionable = "actionable"
    Branch = "branch"
    Link = "link"
    Note = "note"
    Title = "title"
    Spacer = "spacer"
