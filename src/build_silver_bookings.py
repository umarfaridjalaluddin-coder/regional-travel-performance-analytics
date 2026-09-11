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

    result = result.merge(
        product_mapping.rename(
            columns={
                "country_code":
                    "source_country",
                "source_product":
                    "product_type_source",
            }
        ),
        on=[
            "source_country",
            "product_type_source",
        ],
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        channel_mapping.rename(
            columns={
                "country_code":
                    "source_country",
                "source_channel":
                    "booking_channel_source",
            }
        ),
        on=[
            "source_country",
            "booking_channel_source",
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
            in customer_keys[country]
        )

        supplier_valid.append(
            supplier_id is not None
            and supplier_id
            in supplier_keys[country]
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
        ].notna()
    )

    result[
        "customer_id_present"
    ] = (
        result[
            "customer_id_local"
        ].notna()
    )

    result[
        "supplier_id_present"
    ] = (
        result[
            "supplier_id_local"
        ].notna()
    )

    result[
        "product_mapping_valid"
    ] = (
        result[
            "regional_product"
        ].notna()
    )

    result[
        "channel_mapping_valid"
    ] = (
        result[
            "regional_channel"
        ].notna()
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
        ].notna()
        &
        (
            result[
                "booking_value_local"
            ]
            >= 0
        )
    )

    result[
        "booking_date_valid"
    ] = (
        result[
            "booking_date"
        ].notna()
    )

    result[
        "travel_date_valid"
    ] = (
        result[
            "travel_date"
        ].notna()
        &
        result[
            "booking_date"
        ].notna()
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
    ] = result[
        "booking_status"
    ].isin(
        [
            "Confirmed",
            "Cancelled",
            "Refunded",
        ]
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
        "supplier_id_local",
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
        "supplier_id_local",
        "product_type_source",
        "booking_channel_source",
        "transaction_currency",
        "booking_value_local",
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


def main() -> None:

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    staging = load_staging()

    raw_row_count = len(
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

    accepted_count = len(
        clean
    )

    rejected_count = len(
        quarantine
    )

    reconciled_count = (
        accepted_count
        + rejected_count
    )

    print(
        "\nSilver processing completed."
    )

    print(
        f"\nInput staging rows: "
        f"{raw_row_count:,}"
    )

    print(
        f"Accepted rows:      "
        f"{accepted_count:,}"
    )

    print(
        f"Quarantined rows:   "
        f"{rejected_count:,}"
    )

    print(
        f"Reconciled rows:    "
        f"{reconciled_count:,}"
    )

    if reconciled_count != raw_row_count:
        raise RuntimeError(
            "Row reconciliation failed."
        )

    print(
        "\nAccepted by country:"
    )

    print(
        clean[
            "source_country"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        "\nQuarantined by country:"
    )

    if quarantine.empty:
        print("None")

    else:
        print(
            quarantine[
                "source_country"
            ]
            .value_counts()
            .sort_index()
            .to_string()
        )

    print(
        "\nRejection reasons:"
    )

    if rejection_summary.empty:
        print("None")

    else:
        print(
            rejection_summary.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()