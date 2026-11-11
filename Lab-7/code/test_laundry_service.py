"""Lab 7 - Fuzz testing laundry_service with Hypothesis.

The property under test for all three functions is the one from the handout:
given any input at all, the function must not crash. A function that cannot
parse what it was handed should say so by returning None, not by letting a
ValueError or AttributeError escape to the caller.

Each function also gets stronger properties beyond "no crash", because a
function that always returned None would pass the crash test while being
useless.

    pytest test_laundry_service.py
"""

import math

from hypothesis import given, strategies as st

from laundry_service import parse_order, weight_average, payable_charge


# Anything a caller might realistically pass in, including the wrong type.
ANY_INPUT = (
    st.text()
    | st.none()
    | st.integers()
    | st.floats()
    | st.booleans()
    | st.lists(st.text())
    | st.binary()
)


# ------------------------------------------------------------- parse_order

@given(ANY_INPUT)
def test_parse_order_no_crash(s):
    """No input of any type may raise."""
    try:
        parse_order(s)
    except Exception as exc:                      # noqa: BLE001 - that is the point
        raise AssertionError(
            f"parse_order crashed on {s!r} with {type(exc).__name__}: {exc}"
        ) from exc


@given(ANY_INPUT)
def test_parse_order_shape(s):
    """The result is either None or a (name, weight) pair worth trusting."""
    result = parse_order(s)
    if result is None:
        return
    garment, kg = result
    assert isinstance(garment, str) and garment != ""
    assert isinstance(kg, float)
    assert math.isfinite(kg), "a weight of nan or inf should have been rejected"
    assert kg >= 0, "a negative weight should have been rejected"


@given(st.sampled_from(["regular", "delicate", "bedding"]),
       st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
def test_parse_order_accepts_well_formed_orders(garment, kg):
    """Valid input must still parse - hardening must not reject everything."""
    result = parse_order(f"{garment}: {kg}")
    assert result is not None
    assert result[0] == garment.title()
    assert math.isclose(result[1], kg)


# ---------------------------------------------------------- weight_average

@given(ANY_INPUT)
def test_weight_average_no_crash(s):
    """No input of any type may raise."""
    try:
        weight_average(s)
    except Exception as exc:                      # noqa: BLE001
        raise AssertionError(
            f"weight_average crashed on {s!r} with {type(exc).__name__}: {exc}"
        ) from exc


@given(st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=1))
def test_weight_average_lies_between_min_and_max(values):
    """A mean has to sit inside the range of what it averaged."""
    result = weight_average(",".join(str(v) for v in values))
    assert result is not None
    assert min(values) <= result <= max(values)


@given(st.integers(min_value=-10_000, max_value=10_000))
def test_weight_average_of_one_value_is_that_value(value):
    assert weight_average(str(value)) == value


# --------------------------------------------------------- payable_charge

@given(ANY_INPUT)
def test_payable_charge_no_crash(s):
    """No input of any type may raise."""
    try:
        payable_charge(s)
    except Exception as exc:                      # noqa: BLE001
        raise AssertionError(
            f"payable_charge crashed on {s!r} with {type(exc).__name__}: {exc}"
        ) from exc


@given(ANY_INPUT)
def test_payable_charge_is_never_negative_or_nan(s):
    """The headline guarantee: you never owe a negative or nonsensical amount."""
    result = payable_charge(s)
    if result is None:
        return
    assert isinstance(result, float)
    assert not math.isnan(result), "nan leaked through max(total, 0)"
    assert math.isfinite(result), "inf is not a payable charge"
    assert result >= 0


@given(st.floats(min_value=0, max_value=100_000, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0, max_value=100_000, allow_nan=False, allow_infinity=False))
def test_payable_charge_applies_tax_then_discount(charge, discount):
    """Valid input must still compute the documented formula."""
    result = payable_charge(f"{charge}|{discount}")
    assert result is not None
    assert math.isclose(result, max(charge * 1.18 - discount, 0), rel_tol=1e-9)
