
import pytest

from photo_print_order import (
    extra_print_charge,
    order_valid,
    dispatch_status
)


# =====================================================
# 1. BRANCH TESTS: extra_print_charge()
# =====================================================

def test_invalid_print_size_branch():
    with pytest.raises(ValueError):
        extra_print_charge("10x12", 20, "matte", False)


def test_valid_print_size_branch():
    assert extra_print_charge("4x6", 20, "matte", False) == 0


def test_negative_copies_branch():
    with pytest.raises(ValueError):
        extra_print_charge("4x6", -1, "matte", False)


def test_non_negative_copies_branch():
    assert extra_print_charge("4x6", 20, "matte", False) == 0


def test_member_and_eligible_size_branch():
    # is_member = True and print_size != 8x10
    assert extra_print_charge("4x6", 25, "matte", True) == 0


def test_non_member_branch():
    # is_member = False
    assert extra_print_charge("4x6", 20, "matte", False) == 0


def test_member_with_8x10_branch():
    # is_member = True, but print_size == 8x10
    assert extra_print_charge("8x10", 10, "matte", True) == 0


def test_extra_prints_zero_or_less_branch():
    assert extra_print_charge("5x7", 15, "matte", False) == 0


def test_extra_prints_greater_than_zero_branch():
    assert extra_print_charge("5x7", 16, "matte", False) == 4


def test_matte_finish_branch():
    assert extra_print_charge("4x6", 21, "matte", False) == 4


def test_non_matte_finish_branch():
    assert extra_print_charge("4x6", 21, "glossy", False) == 7


def test_extra_prints_not_greater_than_50():
    # Exactly 50 extra prints
    assert extra_print_charge("4x6", 70, "matte", False) == 200


def test_extra_prints_greater_than_50():
    # 51 extra prints, rate becomes 4 + 2
    assert extra_print_charge("4x6", 71, "matte", False) == 306


def test_canvas_finish_branch():
    # Canvas adds another Rs. 5 when extra > 50
    assert extra_print_charge("4x6", 71, "canvas", False) == 714


# =====================================================
# 2. BRANCH TESTS: order_valid()
# =====================================================

def test_rush_order_true_branch():
    assert order_valid(10, 50, True) is True


def test_rush_order_false_branch():
    assert order_valid(10, 51, True) is False


def test_non_rush_order_branch():
    assert order_valid(10, 100, False) is True


def test_file_size_greater_than_25_branch():
    assert order_valid(26, 100, False) is False


def test_file_size_not_greater_than_25_branch():
    assert order_valid(25, 100, False) is True


def test_copies_within_500_branch():
    assert order_valid(10, 500, False) is True


def test_copies_greater_than_500_branch():
    assert order_valid(10, 501, False) is False


# =====================================================
# 3. BRANCH TESTS: dispatch_status()
# =====================================================

def test_framed_order_branch():
    # Framed order has cutoff of 24 hours.
    assert dispatch_status(24, True, False) == "on_time"


def test_unframed_order_branch():
    # Unframed order has cutoff of 12 hours.
    assert dispatch_status(12, False, False) == "on_time"


def test_international_order_branch():
    # Framed + international = 24 + 24 = 48 hours.
    assert dispatch_status(48, True, True) == "on_time"


def test_domestic_order_branch():
    # Unframed + domestic = 12 hours.
    assert dispatch_status(12, False, False) == "on_time"


def test_hours_greater_than_cutoff_branch():
    assert dispatch_status(30, True, False) == "on_time"


def test_hours_less_than_cutoff_but_tight_branch():
    # Framed domestic cutoff = 24.
    # 18 hours is exactly cutoff - 6.
    assert dispatch_status(18, True, False) == "tight"


def test_hours_below_tight_window_branch():
    # Below 18 hours for framed domestic order.
    assert dispatch_status(17, True, False) == "missed"
