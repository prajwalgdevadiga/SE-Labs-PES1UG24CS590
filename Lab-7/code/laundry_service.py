"""Laundry order parsing and charging, hardened against malformed input.

Every public function here follows one rule, which is the property the
Hypothesis suite checks: whatever you pass in, it returns a result or it
returns None. It never raises. Callers test for None rather than catching
exceptions from a parser.
"""

import math

TAX_MULTIPLIER = 1.18


def parse_order(text):
    """Parse "garment: weight" into (Garment, weight_kg).

    Returns None if text is not a string, is not exactly one colon-separated
    pair, has an empty garment name, or carries a weight that is not a finite
    number of kilograms at or above zero.
    """
    if not isinstance(text, str):
        return None

    parts = text.split(":")
    if len(parts) != 2:
        return None

    garment, raw_kg = parts[0].strip(), parts[1].strip()
    if not garment:
        return None

    try:
        kg = float(raw_kg)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(kg) or kg < 0:
        return None

    return garment.title(), kg


def weight_average(weights_csv):
    """Average a comma-separated list of whole-kilogram weights.

    Returns None if the input is not a string or any field is not an integer.
    Rounds to nearest rather than flooring, so the result of averaging
    negatives is not dragged away from the true mean.
    """
    if not isinstance(weights_csv, str):
        return None

    fields = [field.strip() for field in weights_csv.split(",")]
    if not fields or any(field == "" for field in fields):
        return None

    values = []
    for field in fields:
        try:
            values.append(int(field))
        except (TypeError, ValueError):
            return None

    # round-half-to-even on the exact quotient, so the mean always lands
    # between min and max instead of flooring below it for negatives
    return round(sum(values) / len(values))


def payable_charge(text):
    """Work out "charge|discount" as charge * 1.18 - discount, floored at 0.

    Returns None if the input is not a string, is not exactly one
    pipe-separated pair, or either side is not a finite non-negative number.
    """
    if not isinstance(text, str):
        return None

    parts = text.split("|")
    if len(parts) != 2:
        return None

    try:
        charge = float(parts[0].strip())
        discount = float(parts[1].strip())
    except (TypeError, ValueError):
        return None

    # nan slips through max(total, 0) because every comparison with nan is
    # False, so it has to be rejected before the arithmetic
    if not (math.isfinite(charge) and math.isfinite(discount)):
        return None
    if charge < 0 or discount < 0:
        return None

    total = charge * TAX_MULTIPLIER - discount
    if not math.isfinite(total):
        return None

    return max(total, 0.0)


def main():
    """Prompt for one of each input and report the result."""
    print("==== Running parse_order ====")
    result = parse_order(input("Enter garment:weight in kg (e.g. regular:6): "))
    if result is None:
        print("Could not read that as garment:weight - skipping.")
    else:
        print("Garment and Weight:", result)

    print("\n==== Running weight_average ====")
    result = weight_average(input("Enter garment weights as CSV (e.g. 3,5,8): "))
    if result is None:
        print("Could not read that as a list of whole weights - skipping.")
    else:
        print("Average Weight:", result)

    print("\n==== Running payable_charge ====")
    result = payable_charge(input("Enter charge|discount (e.g. 300|40): "))
    if result is None:
        print("Could not read that as charge|discount - skipping.")
    else:
        print("Payable Charge:", result)


if __name__ == "__main__":
    main()
