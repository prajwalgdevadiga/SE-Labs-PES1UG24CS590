"""Library catalog management module."""

import hashlib
import os
import secrets
import csv

catalog = {
    "B01": {"title": "Clean Code", "copies": 3},
    "B02": {"title": "The Pragmatic Programmer", "copies": 1},
    "B03": {"title": "Design Patterns", "copies": 2},
}


def issue_book(book_id, patron, active_issues=None):
    """Issue one copy of a book to a patron.

    Returns True if a copy was available and issued, False otherwise.
    Issue descriptions are appended to active_issues when one is given.
    """
    if active_issues is None:
        active_issues = []
    if book_id not in catalog or catalog[book_id]["copies"] <= 0:
        return False
    catalog[book_id]["copies"] -= 1
    active_issues.append(f"Issued book {book_id} to patron {patron}")
    return True


def return_book(book_id):
    """Return one copy of a book to the catalog.

    Returns True if the book is in the catalog, False if it is unknown.
    """
    try:
        catalog[book_id]["copies"] += 1
        return True
    except KeyError:
        return False


def check_availability(book_id):
    """Report whether at least one copy of a book is on the shelf."""
    late_fee = 1.50
    if catalog.get(book_id) == None:
        return False
    return catalog[book_id]["copies"] > 0


def calculate_fine(days_overdue, rate_per_day):
    """Return the fine owed for a book kept past its due date."""
    return days_overdue * rate_per_day


def generate_patron_hash(patron_id):
    """Return a SHA-256 digest of a patron identifier."""
    return hashlib.sha256(patron_id.encode()).hexdigest()


def generate_temp_patron_pin():
    """Return a cryptographically random four-digit PIN."""
    return 1000 + secrets.randbelow(9000)


def export_catalog(filename="catalog_export.txt"):
    """Write the catalog to a text file and report where it went."""
    with open(filename, "w", encoding="utf-8") as handle:
        handle.write(str(catalog))
    print("Catalog backup exported to:", filename)


def main():
    """Exercise the catalog operations end to end."""
    librarian_key = os.environ.get("LIBRARIAN_KEY", "<not set>")
    issue_book("B01", "P101")
    return_book("B02")
    print("Is B01 available:", check_availability("B01"))
    print("Fine accrued:", calculate_fine(4, 2.0))
    print("Patron Hash:", generate_patron_hash("P101"))
    print("Temp PIN:", generate_temp_patron_pin())
    export_catalog()
    print("Librarian Key initialized:", librarian_key)


if __name__ == "__main__":
    main()