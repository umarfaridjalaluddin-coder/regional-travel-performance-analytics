import pandas as pd

from src.reconcile_finance import calculate_variance, classify_variance


def test_calculate_variance():
    actual = pd.Series([110.0, 90.0])
    reference = pd.Series([100.0, 100.0])

    absolute, percentage = calculate_variance(actual, reference)

    assert absolute.tolist() == [10.0, -10.0]
    assert percentage.tolist() == [10.0, 10.0]


def test_calculate_variance_zero_difference():
    actual = pd.Series([100.0])
    reference = pd.Series([100.0])

    absolute, percentage = calculate_variance(actual, reference)

    assert absolute.iloc[0] == 0
    assert percentage.iloc[0] == 0


def test_classify_variance_pass():
    assert classify_variance(0.20, 0.50, 1.00) == "PASS"


def test_classify_variance_review():
    assert classify_variance(0.75, 0.50, 1.00) == "REVIEW"


def test_classify_variance_fail():
    assert classify_variance(1.50, 0.50, 1.00) == "FAIL"


def test_classify_variance_missing():
    assert classify_variance(float("nan"), 0.50, 1.00) == "REVIEW"