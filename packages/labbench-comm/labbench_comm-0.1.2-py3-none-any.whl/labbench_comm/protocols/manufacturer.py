from enum import IntEnum


class Manufacturer(IntEnum):
    """
    Manufacturer identifiers (MID).

    Values are defined to match embedded firmware expectations
    and are compatible with 32-bit unsigned integer storage.
    """

    #: Invalid MID, used to signal an error.
    Invalid = 0

    #: Inventors' Way ApS
    InventorsWay = 1

    #: Detectronic A/S
    Detectronic = 2

    #: Nocitech ApS
    Nocitech = 3

    #: InnoCon Medical ApS
    InnoCon = 4

    #: Nordic-NeuroSTIM ApS
    NordicNeuroSTIM = 5

    #: Banrob ApS
    Banrob = 6

    #: Use only for testing purposes.
    #: Please contact Inventors' Way at info@inventors.dk to get an MID allocated.
    Generic = 0xFFFFFFFF
