"""Lab 6 - Branch (decision) coverage test suite for laundry_service.

Goal: make every decision in laundry_service.py evaluate both True and False.

The statement suite already reached 100% line coverage but only 98% branch,
with one partial: `21->23`, the `if speed == "express"` nested inside
`if extra > 10`. Its False path falls straight through to line 23, which the
True path already reaches -- so every line looked covered while that decision
had only ever been taken one way. Covering it needs an order that is more
than 10 kg over the allowance at *standard* speed.

Alongside that, each decision here is driven from both sides and the
comparisons are pinned at their boundaries, since `<=`, `>` and `>=` are
where off-by-one errors live.

    coverage run --branch -m pytest BranchCoverageTest_41_laundry_service.py
    coverage report -m
"""

import pytest

from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# ============================================================ extra_weight_charge

# --- decision: garment_type not in INCLUDED_KG -------------------------------

def test_unknown_garment_type_raises():
    """True side: the type is not in the table."""
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("silk", 4, "standard", False)


@pytest.mark.parametrize("garment", ["regular", "delicate", "bedding"])
def test_every_known_garment_type_is_accepted(garment):
    """False side, for all three known types."""
    assert extra_weight_charge(garment, 0, "standard", False) == 0


# --- decision: weight_kg < 0 -------------------------------------------------

def test_negative_weight_raises():
    """True side."""
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_zero_weight_is_valid():
    """False side at the boundary -- 0 is not negative."""
    assert extra_weight_charge("regular", 0, "standard", False) == 0


# --- decision: is_member and garment_type != "bedding" -----------------------
# A compound condition, so each operand is driven both ways.

def test_member_with_non_bedding_gets_the_bonus_allowance():
    """Both operands True -> allowance 5 + 2 = 7 kg."""
    # 7 kg is exactly the raised allowance, so still nothing to charge
    assert extra_weight_charge("regular", 7, "standard", True) == 0
    # one kilo past it is charged
    assert extra_weight_charge("regular", 8, "standard", True) == 1 * 30


def test_non_member_gets_no_bonus_allowance():
    """First operand False -> allowance stays 5 kg."""
    assert extra_weight_charge("regular", 6, "standard", False) == 1 * 30


def test_member_with_bedding_gets_no_bonus_allowance():
    """Second operand False -> bedding stays at 8 kg even for a member."""
    assert extra_weight_charge("bedding", 8, "standard", True) == 0
    assert extra_weight_charge("bedding", 9, "standard", True) == 1 * 30


# --- decision: extra <= 0 ----------------------------------------------------

def test_exactly_at_the_allowance_is_free():
    """True side at the boundary -- extra == 0."""
    assert extra_weight_charge("delicate", 3, "standard", False) == 0


def test_one_kilo_over_the_allowance_is_charged():
    """False side at the boundary -- extra == 1."""
    assert extra_weight_charge("delicate", 4, "standard", False) == 1 * 30


# --- decision: speed == "standard" -------------------------------------------

def test_standard_speed_uses_the_lower_rate():
    """True side -> 30 per kg."""
    assert extra_weight_charge("regular", 10, "standard", False) == 5 * 30


def test_express_speed_uses_the_higher_rate():
    """False side -> 50 per kg."""
    assert extra_weight_charge("regular", 10, "express", False) == 5 * 50


def test_any_other_speed_is_treated_as_non_standard():
    """False side again -- the else is a catch-all, not an express-only path."""
    assert extra_weight_charge("regular", 10, "overnight", False) == 5 * 50


# --- decision: extra > 10 ----------------------------------------------------

def test_exactly_ten_kilos_over_avoids_the_surcharge():
    """False side at the boundary -- 10 is not > 10."""
    assert extra_weight_charge("regular", 15, "standard", False) == 10 * 30


def test_eleven_kilos_over_triggers_the_surcharge():
    """True side at the boundary -- rate 30 + 15."""
    assert extra_weight_charge("regular", 16, "standard", False) == 11 * 45


# --- decision: speed == "express" (nested) -----------------------------------
# This is the branch the statement suite missed (partial 21->23).

def test_large_excess_at_standard_speed_skips_the_express_topup():
    """False side -- THE GAP the line-coverage suite left open.

    30 (standard) + 15 (over 10 kg) = 45 per kg, with no express top-up.
    """
    assert extra_weight_charge("regular", 20, "standard", False) == 15 * 45


def test_large_excess_at_express_speed_adds_the_topup():
    """True side -- 50 + 15 + 10 = 75 per kg."""
    assert extra_weight_charge("regular", 20, "express", False) == 15 * 75


def test_large_excess_at_another_non_standard_speed_skips_the_topup():
    """False side via a speed that is neither standard nor express."""
    # 50 (non-standard) + 15 (over 10 kg), but no express top-up
    assert extra_weight_charge("regular", 20, "overnight", False) == 15 * 65


# ============================================================== order_acceptable

# --- decision: is_delicate ---------------------------------------------------

def test_delicate_order_at_the_item_limit_is_accepted():
    """True side, boundary -- 5 items is allowed."""
    assert order_acceptable(1, 5, True) is True


def test_delicate_order_over_the_item_limit_is_rejected():
    """True side, boundary -- 6 items is not."""
    assert order_acceptable(1, 6, True) is False


def test_delicate_order_ignores_the_weight_cap():
    """True side -- the weight check is never reached for delicates."""
    assert order_acceptable(100, 3, True) is True


# --- decision: weight_kg > 25 ------------------------------------------------

def test_non_delicate_order_at_the_weight_cap_is_accepted():
    """False side, boundary -- 25 kg is not over the cap."""
    assert order_acceptable(25, 10, False) is True


def test_non_delicate_order_over_the_weight_cap_is_rejected():
    """True side, boundary -- 26 kg is."""
    assert order_acceptable(26, 10, False) is False


# --- final return: items <= 40 -----------------------------------------------

def test_non_delicate_order_at_the_item_limit_is_accepted():
    """Boundary -- 40 items is allowed."""
    assert order_acceptable(10, 40, False) is True


def test_non_delicate_order_over_the_item_limit_is_rejected():
    """Boundary -- 41 items is not."""
    assert order_acceptable(10, 41, False) is False


# =============================================================== dropoff_status

# --- decision: has_bedding ---------------------------------------------------

def test_bedding_raises_the_cutoff_to_ninety():
    """True side -- 80 minutes clears 60 but not the bedding cutoff of 90."""
    assert dropoff_status(80, True, False) == "late"


def test_no_bedding_uses_the_sixty_minute_cutoff():
    """False side -- the same 80 minutes is comfortably accepted."""
    assert dropoff_status(80, False, False) == "accepted"


# --- decision: is_express ----------------------------------------------------

def test_express_adds_thirty_minutes_to_the_cutoff():
    """True side -- cutoff 60 + 30 = 90, so 80 minutes is only "late"."""
    assert dropoff_status(80, False, True) == "late"


def test_non_express_leaves_the_cutoff_alone():
    """False side -- already covered above, pinned here explicitly."""
    assert dropoff_status(60, False, False) == "accepted"


def test_bedding_and_express_together_give_the_highest_cutoff():
    """Both True -- 90 + 30 = 120."""
    assert dropoff_status(120, True, True) == "accepted"
    assert dropoff_status(119, True, True) == "late"


# --- decision: minutes_before_closing >= cutoff ------------------------------

def test_exactly_at_the_cutoff_is_accepted():
    """True side, boundary."""
    assert dropoff_status(60, False, False) == "accepted"


def test_one_minute_inside_the_cutoff_is_not_accepted():
    """False side, boundary."""
    assert dropoff_status(59, False, False) == "late"


# --- decision: minutes_before_closing >= cutoff - 20 -------------------------

def test_at_the_edge_of_the_grace_window_is_late():
    """True side, boundary -- cutoff 60, grace floor 40."""
    assert dropoff_status(40, False, False) == "late"


def test_past_the_grace_window_is_rejected():
    """False side, boundary -- one minute below the floor."""
    assert dropoff_status(39, False, False) == "rejected"


def test_well_past_the_grace_window_is_rejected():
    """False side, clearly outside."""
    assert dropoff_status(0, True, True) == "rejected"
