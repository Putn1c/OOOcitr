import pytest

from calculator import (
    COMPLEXITY_COEF,
    REGION_COEF,
    calculate,
    normative_deadline,
)


def test_deadline_boundary_small_area():
    assert normative_deadline("geodesic", 10) == 15
    assert normative_deadline("geodesic", 10.1) == 30


def test_deadline_upper_bucket():
    assert normative_deadline("geodesic", 1000) == 90


def test_deadline_unknown_type():
    with pytest.raises(ValueError):
        normative_deadline("unknown", 10)


def test_calculate_cost_positive():
    result = calculate("geodesic", 20, "medium", "moscow")
    expected = (50000 + 1500 * 20) * COMPLEXITY_COEF["medium"] * REGION_COEF["moscow"]
    assert result["cost_rub"] == pytest.approx(expected, rel=1e-6)


def test_calculate_deadline_in_result():
    result = calculate("geological", 60, "simple", "mo")
    assert result["deadline_days"] == 60  # bucket 50 < 60 ≤ 100


def test_calculate_invalid_area():
    with pytest.raises(ValueError):
        calculate("geodesic", 0, "simple", "mo")


def test_calculate_invalid_complexity():
    with pytest.raises(ValueError):
        calculate("geodesic", 10, "super-hard", "mo")
