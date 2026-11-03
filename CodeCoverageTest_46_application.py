
import pytest

from photo_print_order import (
    extra_print_charge,
    order_valid,
    dispatch_status
)


# =====================================================
# 1. TEST CASES FOR extra_print_charge()
# =====================================================

def test_invalid_print_size():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("10x12", 20, "matte", False)


def test_negative_copies():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -5, "matte", False)


def test_non_member_within_included_prints():
    assert extra_print_charge("4x6", 20, "matte", False) == 0


def test_member_within_included_prints():
    # Members get 5 additional included prints for 4x6.
    assert extra_print_charge("4x6", 25, "matte", True) == 0


def test_member_8x10_no_extra_included_prints():
    # Membership does not increase the included 8x10 prints.
    assert extra_print_charge("8x10", 10, "matte", True) == 0


def test_matte_extra_print_charge():
    # 1 extra print * Rs. 4
    assert extra_print_charge("4x6", 21, "matte", False) == 4


def test_non_matte_extra_print_charge():
    # Non-matte finish uses the default rate of Rs. 7.
    assert extra_print_charge("4x6", 21, "glossy", False) == 7


def test_more_than_50_extra_matte_prints():
    # 51 extra prints * (Rs. 4 + Rs. 2)
    assert extra_print_charge("4x6", 71, "matte", False) == 306


def test_more_than_50_extra_canvas_prints():
    # 51 extra prints * (Rs. 7 + Rs. 2 + Rs. 5)
    assert extra_print_charge("4x6", 71, "canvas", False) == 714


# =====================================================
# 2. TEST CASES FOR order_valid()
# =====================================================

def test_valid_rush_order():
    assert order_valid(10, 50, True) is True


def test_invalid_rush_order():
    assert order_valid(10, 51, True) is False


def test_normal_order_file_size_exceeded():
    assert order_valid(30, 100, False) is False


def test_normal_order_valid():
    assert order_valid(20, 100, False) is True


def test_normal_order_maximum_copies():
    assert order_valid(20, 500, False) is True


def test_normal_order_exceeds_copy_limit():
    assert order_valid(20, 501, False) is False


# =====================================================
# 3. TEST CASES FOR dispatch_status()
# =====================================================

def test_framed_international_order_on_time():
    # Cutoff = 24 + 24 = 48 hours.
    assert dispatch_status(48, True, True) == "on_time"


def test_framed_international_order_tight():
    # 42 hours is exactly 6 hours before the cutoff.
    assert dispatch_status(42, True, True) == "tight"


def test_framed_international_order_missed():
    # 41 hours is below the tight window.
    assert dispatch_status(41, True, True) == "missed"


def test_unframed_domestic_order_on_time():
    # Cutoff = 12 hours.
    assert dispatch_status(12, False, False) == "on_time"
