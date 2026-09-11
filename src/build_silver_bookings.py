from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGING_PATH = (
    PROJECT_ROOT
    / "data"
    / "staging"
    / "bookings_regional.parquet"
)

REFERENCE_DIR = (
    PROJECT_ROOT
    / "data"
    / "reference"
)

SILVER_DIR = (
    PROJECT_ROOT
    / "data"
    / "silver"
)

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


def load_staging() -> pd.DataFrame:
    return pd.read_parquet(
        STAGING_PATH
    )


def load_reference_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    product_mapping = pd.read_csv(
        REFERENCE_DIR
        / "product_mapping.csv"
    )

    channel_mapping = pd.read_csv(
        REFERENCE_DIR
        / "channel_mapping.csv"
    )

    return (
        product_mapping,
        channel_mapping,
    )


def load_customer_keys() -> dict[str, set[str]]:
    return {
        "MY": set(
            pd.read_excel(
                RAW_DIR
                / "malaysia"
                / "customers.xlsx"
            )[
                "customer_id"
            ]
            .dropna()
            .astype(str)
        ),
        "SG": set(
            pd.read_csv(
                RAW_DIR
                / "singapore"
                / "client_master.csv"
            )[
                "client_code"
            ]
            .dropna()
            .astype(str)
        ),
        "ID": set(
            pd.read_excel(
                RAW_DIR
                / "indonesia"
                / "accounts.xlsx"
            )[
                "account_no"
            ]
            .dropna()
            .astype(str)
        ),
    }


def load_supplier_keys() -> dict[str, set[str]]:
    return {
        "MY": set(
            pd.read_csv(
                RAW_DIR
                / "malaysia"
                / "suppliers.csv"
            )[
                "supplier_id"
            ]
            .dropna()
            .astype(str)
        ),
        "SG": set(
            pd.read_excel(
                RAW_DIR
                / "singapore"
                / "vendor_master.xlsx"
            )[
                "vendor_code"
            ]
            .dropna()
            .astype(str)
        ),
        "ID": set(
            pd.read_csv(
                RAW_DIR
                / "indonesia"
                / "supplier_export.csv"
            )[
                "provider_code"
            ]
            .dropna()
            .astype(str)
        ),
    }


def expected_currency(
    country_code: str,
) -> str:
    return {
        "MY": "MYR",
        "SG": "SGD",
        "ID": "IDR",
    }[country_code]


def add_mapping_columns(
    df: pd.DataFrame,
    product_mapping: pd.DataFrame,
    channel_mapping: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    product_map = (
        product_mapping
        .rename(
            columns={
                "country_code":
                    "source_country",
                "source_product":
                    "product_type_source",
            }
        )
        .copy()
    )

    channel_map = (
        channel_mapping
        .rename(
            columns={
                "country_code":
                    "source_country",
                "source_channel":
                    "booking_channel_source",
            }
        )
        .copy()
    )

    result = result.merge(
        product_map,
        on=[
            "source_country",
            "product_type_source",
        ],
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        channel_map,
        on=[
            "source_country",
            "booking_channel_source",
        ],
        how="left",
        validate="many_to_one",
    )

    return result


def add_regional_master_ids(
    df: pd.DataFrame,
) -> pd.DataFrame:

    customer_crosswalk = pd.read_csv(
        REFERENCE_DIR
        / "customer_crosswalk.csv"
    )

    supplier_crosswalk = pd.read_csv(
        REFERENCE_DIR
        / "supplier_crosswalk.csv"
    )

    customer_lookup = (
        customer_crosswalk[
            [
                "source_country",
                "local_customer_id",
                "regional_customer_id",
            ]
        ]
        .rename(
            columns={
                "local_customer_id":
                    "customer_id_local"
            }
        )
        .copy()
    )

    supplier_lookup = (
        supplier_crosswalk[
            [
                "source_country",
                "local_supplier_id",
                "regional_supplier_id",
            ]
        ]
        .rename(
            columns={
                "local_supplier_id":
                    "supplier_id_local"
            }
        )
        .copy()
    )

    result = df.merge(
        customer_lookup,
        on=[
            "source_country",
            "customer_id_local",
        ],
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        supplier_lookup,
        on=[
            "source_country",
            "supplier_id_local",
        ],
        how="left",
        validate="many_to_one",
    )

    return result


def add_reference_checks(
    df: pd.DataFrame,
    customer_keys: dict[str, set[str]],
    supplier_keys: dict[str, set[str]],
) -> pd.DataFrame:

    result = df.copy()

    customer_valid = []
    supplier_valid = []

    for row in result.itertuples(
        index=False
    ):
        country = row.source_country

        customer_id = (
            None
            if pd.isna(
                row.customer_id_local
            )
            else str(
                row.customer_id_local
            )
        )

        supplier_id = (
            None
            if pd.isna(
                row.supplier_id_local
            )
            else str(
                row.supplier_id_local
            )
        )

        customer_valid.append(
            customer_id is not None
            and customer_id
            in customer_keys[
                country
            ]
        )

        supplier_valid.append(
            supplier_id is not None
            and supplier_id
            in supplier_keys[
                country
            ]
        )

    result[
        "customer_reference_valid"
    ] = customer_valid

    result[
        "supplier_reference_valid"
    ] = supplier_valid

    return result


def add_validation_flags(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result[
        "duplicate_booking_id"
    ] = result.duplicated(
        subset=[
            "source_country",
            "booking_id",
        ],
        keep=False,
    )

    result[
        "booking_id_valid"
    ] = (
        result[
            "booking_id"
        ]
        .notna()
    )

    result[
        "customer_id_present"
    ] = (
        result[
            "customer_id_local"
        ]
        .notna()
    )

    result[
        "supplier_id_present"
    ] = (
        result[
            "supplier_id_local"
        ]
        .notna()
    )

    result[
        "regional_customer_valid"
    ] = (
        result[
            "regional_customer_id"
        ]
        .notna()
    )

    result[
        "regional_supplier_valid"
    ] = (
        result[
            "regional_supplier_id"
        ]
        .notna()
    )

    result[
        "product_mapping_valid"
    ] = (
        result[
            "regional_product"
        ]
        .notna()
    )

    result[
        "channel_mapping_valid"
    ] = (
        result[
            "regional_channel"
        ]
        .notna()
    )

    result[
        "currency_valid"
    ] = result.apply(
        lambda row:
            row[
                "transaction_currency"
            ]
            == expected_currency(
                row[
                    "source_country"
                ]
            ),
        axis=1,
    )

    result[
        "booking_value_valid"
    ] = (
        result[
            "booking_value_local"
        ]
        .notna()
        &
        (
            result[
                "booking_value_local"
            ]
            >= 0
        )
    )

    result[
        "revenue_valid"
    ] = (
        result[
            "revenue_local"
        ]
        .notna()
    )

    result[
        "cost_valid"
    ] = (
        result[
            "cost_local"
        ]
        .notna()
    )

    result[
        "booking_date_valid"
    ] = (
        result[
            "booking_date"
        ]
        .notna()
    )

    result[
        "travel_date_valid"
    ] = (
        result[
            "travel_date"
        ]
        .notna()
        &
        result[
            "booking_date"
        ]
        .notna()
        &
        (
            result[
                "travel_date"
            ]
            >= result[
                "booking_date"
            ]
        )
    )

    result[
        "booking_status_valid"
    ] = (
        result[
            "booking_status"
        ]
        .isin(
            [
                "Confirmed",
                "Cancelled",
                "Refunded",
            ]
        )
    )

    return result


def rejection_reasons(
    row: pd.Series,
) -> list[str]:

    reasons = []

    if not row[
        "booking_id_valid"
    ]:
        reasons.append(
            "MISSING_BOOKING_ID"
        )

    if row[
        "duplicate_booking_id"
    ]:
        reasons.append(
            "DUPLICATE_BOOKING_ID"
        )

    if not row[
        "customer_id_present"
    ]:
        reasons.append(
            "MISSING_CUSTOMER_ID"
        )

    elif not row[
        "customer_reference_valid"
    ]:
        reasons.append(
            "ORPHAN_CUSTOMER"
        )

    elif not row[
        "regional_customer_valid"
    ]:
        reasons.append(
            "UNMAPPED_REGIONAL_CUSTOMER"
        )

    if not row[
        "supplier_id_present"
    ]:
        reasons.append(
            "MISSING_SUPPLIER_ID"
        )

    elif not row[
        "supplier_reference_valid"
    ]:
        reasons.append(
            "ORPHAN_SUPPLIER"
        )

    elif not row[
        "regional_supplier_valid"
    ]:
        reasons.append(
            "UNMAPPED_REGIONAL_SUPPLIER"
        )

    if not row[
        "product_mapping_valid"
    ]:
        reasons.append(
            "UNMAPPED_PRODUCT"
        )

    if not row[
        "channel_mapping_valid"
    ]:
        reasons.append(
            "UNMAPPED_CHANNEL"
        )

    if not row[
        "currency_valid"
    ]:
        reasons.append(
            "INVALID_CURRENCY"
        )

    if not row[
        "booking_value_valid"
    ]:
        reasons.append(
            "INVALID_BOOKING_VALUE"
        )

    if not row[
        "revenue_valid"
    ]:
        reasons.append(
            "INVALID_REVENUE"
        )

    if not row[
        "cost_valid"
    ]:
        reasons.append(
            "INVALID_COST"
        )

    if not row[
        "booking_date_valid"
    ]:
        reasons.append(
            "INVALID_BOOKING_DATE"
        )

    if not row[
        "travel_date_valid"
    ]:
        reasons.append(
            "INVALID_TRAVEL_DATE"
        )

    if not row[
        "booking_status_valid"
    ]:
        reasons.append(
            "INVALID_BOOKING_STATUS"
        )

    return reasons


def classify_records(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result[
        "rejection_reasons"
    ] = result.apply(
        rejection_reasons,
        axis=1,
    )

    result[
        "rejection_reason_count"
    ] = result[
        "rejection_reasons"
    ].str.len()

    result[
        "record_status"
    ] = result[
        "rejection_reason_count"
    ].apply(
        lambda value:
            "ACCEPTED"
            if value == 0
            else "QUARANTINED"
    )

    result[
        "rejection_reasons"
    ] = result[
        "rejection_reasons"
    ].apply(
        lambda values:
            "|".join(values)
    )

    return result


def build_clean_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:

    clean = df.loc[
        df[
            "record_status"
        ]
        == "ACCEPTED"
    ].copy()

    clean[
        "gross_margin_local"
    ] = (
        clean[
            "revenue_local"
        ]
        - clean[
            "cost_local"
        ]
    )

    clean[
        "margin_pct"
    ] = (
        clean[
            "gross_margin_local"
        ]
        .div(
            clean[
                "revenue_local"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
    )

    clean[
        "advance_purchase_days"
    ] = (
        clean[
            "travel_date"
        ]
        - clean[
            "booking_date"
        ]
    ).dt.days

    selected_columns = [
        "source_country",
        "booking_id",
        "booking_date",
        "travel_date",
        "customer_id_local",
        "regional_customer_id",
        "supplier_id_local",
        "regional_supplier_id",
        "product_type_source",
        "regional_product",
        "booking_channel_source",
        "regional_channel",
        "destination_country",
        "transaction_currency",
        "booking_value_local",
        "revenue_local",
        "cost_local",
        "gross_margin_local",
        "margin_pct",
        "advance_purchase_days",
        "booking_status",
        "source_system",
        "source_row_number",
        "staging_loaded_at",
    ]

    return clean[
        selected_columns
    ].copy()


def build_quarantine_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:

    quarantine = df.loc[
        df[
            "record_status"
        ]
        == "QUARANTINED"
    ].copy()

    selected_columns = [
        "source_country",
        "booking_id",
        "customer_id_local",
        "regional_customer_id",
        "supplier_id_local",
        "regional_supplier_id",
        "product_type_source",
        "regional_product",
        "booking_channel_source",
        "regional_channel",
        "transaction_currency",
        "booking_value_local",
        "revenue_local",
        "cost_local",
        "booking_date",
        "travel_date",
        "booking_status",
        "source_system",
        "source_row_number",
        "rejection_reasons",
        "rejection_reason_count",
    ]

    return quarantine[
        selected_columns
    ].copy()


def build_rejection_summary(
    quarantine: pd.DataFrame,
) -> pd.DataFrame:

    if quarantine.empty:
        return pd.DataFrame(
            columns=[
                "source_country",
                "rejection_reason",
                "failed_records",
            ]
        )

    exploded = (
        quarantine[
            [
                "source_country",
                "rejection_reasons",
            ]
        ]
        .assign(
            rejection_reason=lambda x:
                x[
                    "rejection_reasons"
                ].str.split("|")
        )
        .explode(
            "rejection_reason"
        )
    )

    return (
        exploded.groupby(
            [
                "source_country",
                "rejection_reason",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size":
                    "failed_records"
            }
        )
        .sort_values(
            [
                "source_country",
                "failed_records",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )


def build_country_summary(
    classified: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        classified.groupby(
            "source_country",
            as_index=False,
        )
        .agg(
            input_rows=(
                "booking_id",
                "size",
            ),
            accepted_rows=(
                "record_status",
                lambda values:
                    int(
                        (
                            values
                            == "ACCEPTED"
                        ).sum()
                    ),
            ),
            quarantined_rows=(
                "record_status",
                lambda values:
                    int(
                        (
                            values
                            == "QUARANTINED"
                        ).sum()
                    ),
            ),
        )
    )

    summary[
        "acceptance_pct"
    ] = (
        summary[
            "accepted_rows"
        ]
        / summary[
            "input_rows"
        ]
        * 100
    ).round(4)

    summary[
        "quarantine_pct"
    ] = (
        summary[
            "quarantined_rows"
        ]
        / summary[
            "input_rows"
        ]
        * 100
    ).round(4)

    return summary


def validate_clean_dataset(
    clean: pd.DataFrame,
) -> None:

    duplicate_ids = (
        clean.duplicated(
            subset=[
                "source_country",
                "booking_id",
            ],
            keep=False,
        )
        .sum()
    )

    if duplicate_ids > 0:
        raise RuntimeError(
            "Clean Silver contains "
            f"{duplicate_ids} duplicate "
            "booking ID records."
        )

    if (
        clean[
            "customer_id_local"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "missing local customer IDs."
        )

    if (
        clean[
            "regional_customer_id"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "missing regional customer IDs."
        )

    if (
        clean[
            "supplier_id_local"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "missing local supplier IDs."
        )

    if (
        clean[
            "regional_supplier_id"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "missing regional supplier IDs."
        )

    if (
        clean[
            "regional_product"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "unmapped regional products."
        )

    if (
        clean[
            "regional_channel"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Clean Silver contains "
            "unmapped regional channels."
        )

    if (
        clean[
            "booking_value_local"
        ]
        < 0
    ).any():
        raise RuntimeError(
            "Clean Silver contains "
            "negative booking values."
        )

    invalid_dates = (
        clean[
            "travel_date"
        ]
        < clean[
            "booking_date"
        ]
    ).sum()

    if invalid_dates > 0:
        raise RuntimeError(
            "Clean Silver contains "
            f"{invalid_dates} records "
            "where travel date is earlier "
            "than booking date."
        )


def main() -> None:

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    staging = load_staging()

    input_row_count = len(
        staging
    )

    (
        product_mapping,
        channel_mapping,
    ) = load_reference_data()

    customer_keys = (
        load_customer_keys()
    )

    supplier_keys = (
        load_supplier_keys()
    )

    working = add_mapping_columns(
        staging,
        product_mapping,
        channel_mapping,
    )

    working = add_regional_master_ids(
        working
    )

    working = add_reference_checks(
        working,
        customer_keys,
        supplier_keys,
    )

    working = add_validation_flags(
        working
    )

    classified = classify_records(
        working
    )

    clean = build_clean_dataset(
        classified
    )

    quarantine = (
        build_quarantine_dataset(
            classified
        )
    )

    rejection_summary = (
        build_rejection_summary(
            quarantine
        )
    )

    country_summary = (
        build_country_summary(
            classified
        )
    )

    validate_clean_dataset(
        clean
    )

    clean.to_parquet(
        SILVER_DIR
        / "bookings_clean.parquet",
        index=False,
    )

    quarantine.to_parquet(
        SILVER_DIR
        / "bookings_quarantine.parquet",
        index=False,
    )

    rejection_summary.to_csv(
        SILVER_DIR
        / "rejection_summary.csv",
        index=False,
    )

    country_summary.to_csv(
        SILVER_DIR
        / "silver_country_summary.csv",
        index=False,
    )

    accepted_count = len(
        clean
    )

    quarantined_count = len(
        quarantine
    )

    reconciled_count = (
        accepted_count
        + quarantined_count
    )

    print(
        "\nSilver processing completed."
    )

    print(
        "\nRow reconciliation"
    )

    print(
        "------------------"
    )

    print(
        f"Input staging rows: "
        f"{input_row_count:,}"
    )

    print(
        f"Accepted rows:      "
        f"{accepted_count:,}"
    )

    print(
        f"Quarantined rows:   "
        f"{quarantined_count:,}"
    )

    print(
        f"Reconciled rows:    "
        f"{reconciled_count:,}"
    )

    if (
        reconciled_count
        != input_row_count
    ):
        raise RuntimeError(
            "Row reconciliation failed. "
            "Accepted + quarantined "
            "does not equal input."
        )

    print(
        "\nCountry summary"
    )

    print(
        "---------------"
    )

    print(
        country_summary.to_string(
            index=False
        )
    )

    print(
        "\nRejection reasons"
    )

    print(
        "-----------------"
    )

    if rejection_summary.empty:
        print(
            "No rejected records."
        )

    else:
        print(
            rejection_summary.to_string(
                index=False
            )
        )

    print(
        "\nRegional master coverage"
    )

    print(
        "------------------------"
    )

    print(
        "Missing regional customer IDs "
        "in accepted data:",
        clean[
            "regional_customer_id"
        ]
        .isna()
        .sum(),
    )

    print(
        "Missing regional supplier IDs "
        "in accepted data:",
        clean[
            "regional_supplier_id"
        ]
        .isna()
        .sum(),
    )

    print(
        "\nSilver files written to:"
    )

    print(
        SILVER_DIR.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()