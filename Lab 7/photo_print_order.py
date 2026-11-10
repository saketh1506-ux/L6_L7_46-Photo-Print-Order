
INCLUDED_PRINTS = {
    "4x6": 20,
    "5x7": 15,
    "8x10": 10
}

VALID_FINISHES = {"matte", "gloss", "canvas"}


def extra_print_charge(print_size, copies, finish, is_member):
    """
    Calculate the additional charge for prints exceeding the included quantity.

    Raises:
        TypeError: If an argument has an incorrect data type.
        ValueError: If an argument has an invalid value.
    """

    # Validate print size
    if not isinstance(print_size, str):
        raise TypeError("print_size must be a string")

    if print_size not in INCLUDED_PRINTS:
        raise ValueError("unknown print size")

    # Validate copies
    if isinstance(copies, bool) or not isinstance(copies, int):
        raise TypeError("copies must be an integer")

    if copies < 0:
        raise ValueError("invalid copies")

    # Validate finish
    if not isinstance(finish, str):
        raise TypeError("finish must be a string")

    if finish not in VALID_FINISHES:
        raise ValueError("invalid finish")

    # Validate membership
    if not isinstance(is_member, bool):
        raise TypeError("is_member must be a boolean")

    included = INCLUDED_PRINTS[print_size]

    if is_member and print_size != "8x10":
        included += 5

    extra = copies - included

    if extra <= 0:
        return 0

    # Determine rate per additional print
    if finish == "matte":
        rate = 4
    else:
        rate = 7

    # Additional charge for large orders
    if extra > 50:
        rate += 2

        if finish == "canvas":
            rate += 5

    return extra * rate


def order_valid(file_mb, copies, is_rush):
    """
    Validate an order based on file size, copies and rush status.

    Rush orders allow a maximum of 50 copies.
    Normal orders allow a maximum of 500 copies
    and a maximum file size of 25 MB.
    """

    # Validate file size
    if isinstance(file_mb, bool) or not isinstance(file_mb, (int, float)):
        raise TypeError("file_mb must be a number")

    if file_mb < 0:
        raise ValueError("file size cannot be negative")

    # Validate copies
    if isinstance(copies, bool) or not isinstance(copies, int):
        raise TypeError("copies must be an integer")

    if copies < 0:
        raise ValueError("copies cannot be negative")

    # Validate rush status
    if not isinstance(is_rush, bool):
        raise TypeError("is_rush must be a boolean")

    # Rush order validation
    if is_rush:
        return copies <= 50

    # Normal order validation
    if file_mb > 25:
        return False

    return copies <= 500


def dispatch_status(hours_before_dispatch, is_framed, is_international):
    """
    Determine the dispatch status based on available time.

    Returns:
        on_time: Sufficient time is available.
        tight: Dispatch is close to the cutoff.
        missed: The dispatch cutoff has been missed.
    """

    # Validate hours
    if isinstance(hours_before_dispatch, bool) or not isinstance(
        hours_before_dispatch, (int, float)
    ):
        raise TypeError("hours_before_dispatch must be a number")

    if hours_before_dispatch < 0:
        raise ValueError("hours cannot be negative")

    # Validate flags
    if not isinstance(is_framed, bool):
        raise TypeError("is_framed must be a boolean")

    if not isinstance(is_international, bool):
        raise TypeError("is_international must be a boolean")

    # Calculate cutoff
    if is_framed:
        cutoff = 24
    else:
        cutoff = 12

    if is_international:
        cutoff += 24

    # Determine dispatch status
    if hours_before_dispatch >= cutoff:
        return "on_time"

    elif hours_before_dispatch >= cutoff - 6:
        return "tight"

    return "missed"
