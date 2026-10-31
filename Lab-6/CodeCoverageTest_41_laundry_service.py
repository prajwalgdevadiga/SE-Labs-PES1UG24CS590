"""Lab 6 - Code (statement) coverage test suite for laundry_service.

Goal: execute every statement in laundry_service.py at least once.

These tests are written to the question line coverage asks -- "did execution
pass through this line?" -- and nothing more. They reach 100% statement
coverage, which is exactly why they are worth comparing against the branch
suite: a line can be reached without every decision that guards it having
been exercised both ways.

    coverage run -m pytest CodeCoverageTest_41_laundry_service.py
    coverage report -m
"""

import pytest

from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# --------------------------------------------------------------- extra_weight_charge

def test_unknown_garment_type_raises():
    """Reaches the `raise ValueError("unknown garment type")` line."""
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("silk", 4, "standard", False)


def test_negative_weight_raises():
    """Reaches the `raise ValueError("invalid weight")` line."""
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_member_allowance_and_no_extra_weight():
    """Reaches the member allowance bump and the `return 0` line.

    regular includes 5 kg, +2 for members = 7 kg allowed, 4 kg used.
    """
    assert extra_weight_charge("regular", 4, "standard", True) == 0


def test_standard_speed_small_excess():
    """Reaches `rate = 30` and the final return, skipping the surcharge."""
    # regular includes 5 kg, 10 kg used -> 5 kg extra at the standard rate
    assert extra_weight_charge("regular", 10, "standard", False) == 5 * 30


def test_express_speed_large_excess():
    """Reaches `rate = 50`, the >10 kg surcharge and the express top-up."""
    # regular includes 5 kg, 20 kg used -> 15 kg extra
    # rate = 50 (express) + 15 (over 10 kg) + 10 (express top-up) = 75
    assert extra_weight_charge("regular", 20, "express", False) == 15 * 75


# ------------------------------------------------------------------- order_acceptable

def test_delicate_order_within_item_limit():
    """Reaches the delicate branch's return."""
    assert order_acceptable(2, 3, True) is True


def test_heavy_non_delicate_order_rejected():
    """Reaches `return False` for the weight cap."""
    assert order_acceptable(30, 10, False) is False


def test_non_delicate_order_within_item_limit():
    """Reaches the final `return items <= 40`."""
    assert order_acceptable(10, 20, False) is True


# -------------------------------------------------------------------- dropoff_status

def test_bedding_well_before_cutoff_accepted():
    """Reaches `cutoff = 90` and the "accepted" return."""
    assert dropoff_status(120, True, False) == "accepted"


def test_express_raises_the_cutoff():
    """Reaches the `cutoff += 30` line."""
    # no bedding -> 60, express -> 90; 150 minutes is comfortably clear
    assert dropoff_status(150, False, True) == "accepted"


def test_inside_the_grace_window_is_late():
    """Reaches the "late" return."""
    # no bedding, not express -> cutoff 60, grace starts at 40
    assert dropoff_status(50, False, False) == "late"


def test_past_the_grace_window_is_rejected():
    """Reaches the final "rejected" return."""
    assert dropoff_status(30, False, False) == "rejected"
