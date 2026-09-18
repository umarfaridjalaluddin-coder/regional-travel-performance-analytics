import pandas as pd

from src.build_silver_bookings import (
    rejection_reasons,
    classify_records,
)


def make_valid_record():
    """Create one booking where all validation flags pass."""
    return {
        "booking_id_valid": True,
        "duplicate_booking_id": False,
        "customer_id_present": True,
        "customer_reference_valid": True,
        "regional_customer_valid": True,
        "supplier_id_present": True,
        "supplier_reference_valid": True,
        "regional_supplier_valid": True,
        "product_mapping_valid": True,
        "channel_mapping_valid": True,
        "currency_valid": True,
        "booking_value_valid": True,
        "revenue_valid": True,
        "cost_valid": True,
        "booking_date_valid": True,
        "travel_date_valid": True,
        "booking_status_valid": True,
    }


def test_valid_record_has_no_rejection_reason():
    row = pd.Series(make_valid_record())

    reasons = rejection_reasons(row)

    assert reasons == []


def test_valid_record_is_accepted():
    df = pd.DataFrame([make_valid_record()])

    result = classify_records(df)

    assert result.loc[0, "record_status"] == "ACCEPTED"
    assert result.loc[0, "rejection_reason_count"] == 0
    assert result.loc[0, "rejection_reasons"] == ""


def test_missing_booking_id_is_quarantined():
    record = make_valid_record()
    record["booking_id_valid"] = False

    result = classify_records(pd.DataFrame([record]))

    assert result.loc[0, "record_status"] == "QUARANTINED"
    assert result.loc[0, "rejection_reasons"] == "MISSING_BOOKING_ID"


def test_duplicate_booking_is_quarantined():
    record = make_valid_record()
    record["duplicate_booking_id"] = True

    result = classify_records(pd.DataFrame([record]))

    assert result.loc[0, "record_status"] == "QUARANTINED"
    assert "DUPLICATE_BOOKING_ID" in result.loc[0, "rejection_reasons"]


def test_invalid_currency_is_quarantined():
    record = make_valid_record()
    record["currency_valid"] = False

    result = classify_records(pd.DataFrame([record]))

    assert result.loc[0, "record_status"] == "QUARANTINED"
    assert "INVALID_CURRENCY" in result.loc[0, "rejection_reasons"]


def test_missing_customer_and_supplier_are_identified():
    record = make_valid_record()
    record["customer_id_present"] = False
    record["supplier_id_present"] = False

    result = classify_records(pd.DataFrame([record]))

    reasons = result.loc[0, "rejection_reasons"]

    assert result.loc[0, "record_status"] == "QUARANTINED"
    assert result.loc[0, "rejection_reason_count"] == 2
    assert "MISSING_CUSTOMER_ID" in reasons
    assert "MISSING_SUPPLIER_ID" in reasons