from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"


COLUMN_MAPPINGS = {
    "MY": {
        "booking_id": "booking_id",
        "booking_date": "booking_date",
        "travel_date": "travel_date",
        "customer_id": "customer_id_local",
        "supplier_id": "supplier_id_local",
        "product_type": "product_type_source",
        "booking_channel": "booking_channel_source",
        "destination_country": "destination_country",
        "currency": "transaction_currency",
        "booking_value": "booking_value_local",
        "revenue": "revenue_local",
        "cost": "cost_local",
        "booking_status": "booking_status",
    },
    "SG": {
        "transaction_ref": "booking_id",
        "txn_date": "booking_date",
        "departure_date": "travel_date",
        "client_code": "customer_id_local",
        "vendor_code": "supplier_id_local",
        "service_category": "product_type_source",
        "booking_method": "booking_channel_source",
        "destination": "destination_country",
        "txn_currency": "transaction_currency",
        "gross_sales": "booking_value_local",
        "net_revenue": "revenue_local",
        "direct_cost": "cost_local",
        "status": "booking_status",
    },
    "ID": {
        "booking_no": "booking_id",
        "created_at": "booking_date",
        "journey_date": "travel_date",
        "account_no": "customer_id_local",
        "provider_code": "supplier_id_local",
        "travel_product": "product_type_source",
        "channel": "booking_channel_source",
        "destination": "destination_country",
        "currency_code": "transaction_currency",
        "total_booking_amount": "booking_value_local",
        "service_revenue": "revenue_local",
        "supplier_cost": "cost_local",
        "booking_state": "booking_status",
    },
}


def load_raw_bookings(
    country_code: str,
) -> pd.DataFrame:

    if country_code == "MY":
        return pd.read_csv(
            RAW_DIR / "malaysia" / "bookings.csv"
        )

    if country_code == "SG":
        return pd.read_excel(
            RAW_DIR / "singapore" / "transactions.xlsx"
        )

    if country_code == "ID":
        return pd.read_csv(
            RAW_DIR / "indonesia" / "booking_export.csv"
        )

    raise ValueError(
        f"Unsupported country: {country_code}"
    )


def standardise_schema(
    df: pd.DataFrame,
    country_code: str,
) -> pd.DataFrame:

    mapping = COLUMN_MAPPINGS[
        country_code
    ]

    missing_columns = [
        column
        for column in mapping
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{country_code} missing expected columns: "
            f"{missing_columns}"
        )

    staged = (
        df[list(mapping.keys())]
        .rename(columns=mapping)
        .copy()
    )

    staged.insert(
        0,
        "source_country",
        country_code,
    )

    staged["source_system"] = {
        "MY": "MY_BOOKING_EXPORT",
        "SG": "SG_TRANSACTION_EXPORT",
        "ID": "ID_BOOKING_EXPORT",
    }[country_code]

    return staged


def apply_technical_types(
    df: pd.DataFrame,
) -> pd.DataFrame:

    staged = df.copy()

    for column in [
        "booking_date",
        "travel_date",
    ]:
        staged[column] = pd.to_datetime(
            staged[column],
            errors="coerce",
        )

    for column in [
        "booking_value_local",
        "revenue_local",
        "cost_local",
    ]:
        staged[column] = pd.to_numeric(
            staged[column],
            errors="coerce",
        )

    string_columns = [
        "source_country",
        "booking_id",
        "customer_id_local",
        "supplier_id_local",
        "product_type_source",
        "booking_channel_source",
        "destination_country",
        "transaction_currency",
        "booking_status",
        "source_system",
    ]

    for column in string_columns:
        staged[column] = (
            staged[column]
            .astype("string")
        )

    return staged


def add_technical_metadata(
    df: pd.DataFrame,
) -> pd.DataFrame:

    staged = df.copy()

    staged["source_row_number"] = (
        range(1, len(staged) + 1)
    )

    staged["staging_loaded_at"] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )

    return staged


def validate_staging_columns(
    df: pd.DataFrame,
) -> None:

    expected_columns = [
        "source_country",
        "booking_id",
        "booking_date",
        "travel_date",
        "customer_id_local",
        "supplier_id_local",
        "product_type_source",
        "booking_channel_source",
        "destination_country",
        "transaction_currency",
        "booking_value_local",
        "revenue_local",
        "cost_local",
        "booking_status",
        "source_system",
        "source_row_number",
        "staging_loaded_at",
    ]

    actual_columns = list(
        df.columns
    )

    if actual_columns != expected_columns:
        raise ValueError(
            "Unexpected staging schema.\n"
            f"Expected: {expected_columns}\n"
            f"Actual:   {actual_columns}"
        )


def build_country_staging(
    country_code: str,
) -> pd.DataFrame:

    raw = load_raw_bookings(
        country_code
    )

    staged = standardise_schema(
        raw,
        country_code,
    )

    staged = apply_technical_types(
        staged
    )

    staged = add_technical_metadata(
        staged
    )

    validate_staging_columns(
        staged
    )

    print(
        f"{country_code}: "
        f"{len(raw):,} raw rows "
        f"-> {len(staged):,} staging rows"
    )

    return staged


def main() -> None:

    STAGING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    country_frames = []

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:
        staged = (
            build_country_staging(
                country_code
            )
        )

        country_frames.append(
            staged
        )

        staged.to_parquet(
            STAGING_DIR
            / f"bookings_{country_code.lower()}.parquet",
            index=False,
        )

    regional = pd.concat(
        country_frames,
        ignore_index=True,
    )

    validate_staging_columns(
        regional
    )

    regional.to_parquet(
        STAGING_DIR
        / "bookings_regional.parquet",
        index=False,
    )

    print(
        "\nRegional staging completed."
    )

    print(
        f"Total rows: "
        f"{len(regional):,}"
    )

    print(
        "\nRows by country:"
    )

    print(
        regional[
            "source_country"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        "\nStaging files written to:"
    )

    print(
        STAGING_DIR.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()