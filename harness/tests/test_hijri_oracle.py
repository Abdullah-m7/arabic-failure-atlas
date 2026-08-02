import pytest

from atlas.scorers.hijri_oracle import (
    ARABIC_HIJRI_MONTHS,
    gregorian_to_hijri,
    hijri_to_gregorian,
    make_oracle,
    verify_oracle,
)


def test_known_conversion_umm_al_qura():
    assert gregorian_to_hijri("2026-09-15") == "1448-04-04"
    assert hijri_to_gregorian("1448-04-04") == "2026-09-15"


def test_roundtrip():
    for date in ["2026-01-01", "2026-06-30", "2027-03-20"]:
        assert hijri_to_gregorian(gregorian_to_hijri(date)) == date


def test_make_oracle():
    o = make_oracle("2026-09-15")
    assert o == {"type": "hijri", "hijri": "1448-04-04", "gregorian": "2026-09-15"}
    assert verify_oracle(o) == []


def test_hand_written_conversion_is_caught():
    bad = {"type": "hijri", "hijri": "1448-04-05", "gregorian": "2026-09-15"}
    errors = verify_oracle(bad)
    assert errors and "machine-derived" in errors[0]


def test_unknown_oracle_type_rejected():
    assert verify_oracle({"type": "persian", "hijri": "x", "gregorian": "y"})


def test_out_of_range_raises():
    with pytest.raises(Exception):
        gregorian_to_hijri("1500-01-01")  # far outside Umm al-Qura table


def test_month_names_complete():
    assert len(ARABIC_HIJRI_MONTHS) == 12
    assert ARABIC_HIJRI_MONTHS[4] == "ربيع الآخر"
