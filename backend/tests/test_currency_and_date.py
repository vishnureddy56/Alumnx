import pytest
from app.utils.money_parser import parse_indian_money
from app.utils.date_parser import parse_explicit_deadline


def test_money_parser_formats():
    assert parse_indian_money("Indicative budget is Rs. 25 lakhs.") == 2500000
    assert parse_indian_money("Gold tier is ₹4,00,000") == 400000
    assert parse_indian_money("Budget approx 1.2 cr allocated") == 12000000
    assert parse_indian_money("Estimated value: Rs. 6,50,000.") == 650000
    assert parse_indian_money("Deal size around ₹10,00,000") == 1000000
    assert parse_indian_money("Fee is ₹25L") == 2500000
    assert parse_indian_money("No money mentioned here") is None


def test_date_parser_formats():
    due, within_72 = parse_explicit_deadline("Submission due 12th August 2026", "2026-08-01T09:14:22+05:30")
    assert due == "2026-08-12"
    assert within_72 is False

    due_urgent, within_72_urgent = parse_explicit_deadline("Last date for bid submission: 03-08-2026, 1700 hrs IST", "2026-08-01T14:20:00+05:30")
    assert due_urgent == "2026-08-03"
    assert within_72_urgent is True

    due_tom, within_72_tom = parse_explicit_deadline("We need confirmation by tomorrow EOD", "2026-08-02T16:45:00+05:30")
    assert due_tom == "2026-08-03"
    assert within_72_tom is True

    due_vague, _ = parse_explicit_deadline("can we get a demo sometime next week? Nothing urgent.", "2026-08-01T11:02:10+05:30")
    assert due_vague is None
