
import pytest

from hypothesis import given, settings, strategies as st

from photo_print_order import (
    extra_print_charge,
    order_valid,
    dispatch_status
)


# ============================================================
# 1. FUZZ TESTS FOR extra_print_charge()
# ============================================================

@given(
    print_size=st.sampled_from(["4x6", "5x7", "8x10"]),
    copies=st.integers(min_value=0, max_value=1000),
    finish=st.sampled_from(["matte", "gloss", "canvas"]),
    is_member=st.booleans()
)
def test_extra_print_charge_valid_inputs(
    print_size, copies, finish, is_member
):
    result = extra_print_charge(
        print_size, copies, finish, is_member
    )

    assert isinstance(result, int)
    assert result >= 0


@given(
    copies=st.integers(min_value=0, max_value=1000),
    finish=st.sampled_from(["matte", "gloss", "canvas"]),
    is_member=st.booleans()
)
def test_extra_print_charge_within_included_quantity(
    copies, finish, is_member
):
    included = {
        "4x6": 20,
        "5x7": 15,
        "8x10": 10
    }

    for size in included:
        allowed = included[size]

        if is_member and size != "8x10":
            allowed += 5

        if copies <= allowed:
            assert extra_print_charge(
                size, copies, finish, is_member
            ) == 0


@given(
    copies=st.integers(min_value=0, max_value=1000)
)
def test_extra_print_charge_rejects_invalid_print_size(copies):
    with pytest.raises(ValueError):
        extra_print_charge(
            "invalid-size", copies, "matte", False
        )


@given(
    copies=st.integers(max_value=-1)
)
def test_extra_print_charge_rejects_negative_copies(copies):
    with pytest.raises(ValueError):
        extra_print_charge(
            "4x6", copies, "matte", False
        )


@given(
    copies=st.one_of(
        st.text(),
        st.none(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans()
    )
)
def test_extra_print_charge_rejects_invalid_copy_types(copies):
    with pytest.raises(TypeError):
        extra_print_charge(
            "4x6", copies, "matte", False
        )


@given(finish=st.text().filter(
    lambda value: value not in ["matte", "gloss", "canvas"]
))
def test_extra_print_charge_rejects_invalid_finish(finish):
    with pytest.raises(ValueError):
        extra_print_charge(
            "4x6", 30, finish, False
        )


# ============================================================
# 2. FUZZ TESTS FOR order_valid()
# ============================================================

@given(
    file_mb=st.floats(
        min_value=0,
        max_value=1000,
        allow_nan=False,
        allow_infinity=False
    ),
    copies=st.integers(min_value=0, max_value=1000),
    is_rush=st.booleans()
)
def test_order_valid_valid_inputs(file_mb, copies, is_rush):
    result = order_valid(file_mb, copies, is_rush)

    assert isinstance(result, bool)


@given(
    file_mb=st.floats(
        min_value=0,
        max_value=25,
        allow_nan=False,
        allow_infinity=False
    ),
    copies=st.integers(min_value=0, max_value=50)
)
def test_valid_rush_orders(file_mb, copies):
    assert order_valid(file_mb, copies, True) is True


@given(
    file_mb=st.floats(
        min_value=0,
        max_value=1000,
        allow_nan=False,
        allow_infinity=False
    ),
    copies=st.integers(min_value=51, max_value=1000)
)
def test_invalid_rush_orders(file_mb, copies):
    assert order_valid(file_mb, copies, True) is False


@given(
    file_mb=st.floats(
        min_value=0,
        max_value=25,
        allow_nan=False,
        allow_infinity=False
    ),
    copies=st.integers(min_value=0, max_value=500)
)
def test_valid_normal_orders(file_mb, copies):
    assert order_valid(file_mb, copies, False) is True


@given(
    file_mb=st.floats(
        min_value=25.0001,
        max_value=1000,
        allow_nan=False,
        allow_infinity=False
    ),
    copies=st.integers(min_value=0, max_value=500)
)
def test_rejects_large_files_for_normal_orders(file_mb, copies):
    assert order_valid(file_mb, copies, False) is False


@given(copies=st.integers(max_value=-1))
def test_order_valid_rejects_negative_copies(copies):
    with pytest.raises(ValueError):
        order_valid(10, copies, False)


@given(
    file_mb=st.floats(
        min_value=-1000,
        max_value=-0.0001,
        allow_nan=False,
        allow_infinity=False
    )
)
def test_order_valid_rejects_negative_file_size(file_mb):
    with pytest.raises(ValueError):
        order_valid(file_mb, 10, False)


@given(
    file_mb=st.one_of(st.text(), st.none(), st.booleans())
)
def test_order_valid_rejects_invalid_file_types(file_mb):
    with pytest.raises(TypeError):
        order_valid(file_mb, 10, False)


# ============================================================
# 3. FUZZ TESTS FOR dispatch_status()
# ============================================================

@given(
    hours=st.floats(
        min_value=0,
        max_value=500,
        allow_nan=False,
        allow_infinity=False
    ),
    is_framed=st.booleans(),
    is_international=st.booleans()
)
def test_dispatch_status_valid_inputs(
    hours, is_framed, is_international
):
    result = dispatch_status(
        hours, is_framed, is_international
    )

    assert result in ["on_time", "tight", "missed"]


@given(
    hours=st.floats(
        min_value=0,
        max_value=500,
        allow_nan=False,
        allow_infinity=False
    ),
    is_international=st.booleans()
)
def test_framed_dispatch_cutoff(hours, is_international):
    cutoff = 24 + (24 if is_international else 0)

    result = dispatch_status(hours, True, is_international)

    if hours >= cutoff:
        assert result == "on_time"
    elif hours >= cutoff - 6:
        assert result == "tight"
    else:
        assert result == "missed"


@given(
    hours=st.floats(
        min_value=0,
        max_value=500,
        allow_nan=False,
        allow_infinity=False
    ),
    is_international=st.booleans()
)
def test_unframed_dispatch_cutoff(hours, is_international):
    cutoff = 12 + (24 if is_international else 0)

    result = dispatch_status(hours, False, is_international)

    if hours >= cutoff:
        assert result == "on_time"
    elif hours >= cutoff - 6:
        assert result == "tight"
    else:
        assert result == "missed"


@given(
    hours=st.floats(
        min_value=-1000,
        max_value=-0.0001,
        allow_nan=False,
        allow_infinity=False
    )
)
def test_dispatch_status_rejects_negative_hours(hours):
    with pytest.raises(ValueError):
        dispatch_status(hours, False, False)


@given(hours=st.one_of(st.text(), st.none(), st.booleans()))
def test_dispatch_status_rejects_invalid_hour_types(hours):
    with pytest.raises(TypeError):
        dispatch_status(hours, False, False)


# ============================================================
# 4. ADDITIONAL TYPE VALIDATION TESTS
# ============================================================

@given(value=st.one_of(st.text(), st.integers(), st.none()))
def test_extra_print_charge_rejects_invalid_membership_type(value):
    with pytest.raises(TypeError):
        extra_print_charge("4x6", 30, "matte", value)


@given(value=st.one_of(st.text(), st.integers(), st.none()))
def test_order_valid_rejects_invalid_rush_type(value):
    with pytest.raises(TypeError):
        order_valid(10, 100, value)


@given(value=st.one_of(st.text(), st.integers(), st.none()))
def test_dispatch_status_rejects_invalid_framed_type(value):
    with pytest.raises(TypeError):
        dispatch_status(24, value, False)


@given(value=st.one_of(st.text(), st.integers(), st.none()))
def test_dispatch_status_rejects_invalid_international_type(value):
    with pytest.raises(TypeError):
        dispatch_status(24, False, value)
