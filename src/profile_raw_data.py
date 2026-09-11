from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "profiling"

CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.json"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_country_data() -> dict[str, dict[str, pd.DataFrame]]:
    return {
        "MY": {
            "bookings": pd.read_csv(
                RAW_DIR / "malaysia" / "bookings.csv"
            ),
            "customers": pd.read_excel(
                RAW_DIR / "malaysia" / "customers.xlsx"
            ),
            "suppliers": pd.read_csv(
                RAW_DIR / "malaysia" / "suppliers.csv"
            ),
            "finance": pd.read_csv(
                RAW_DIR / "malaysia" / "finance.csv"
            ),
        },
        "SG": {
            "bookings": pd.read_excel(
                RAW_DIR / "singapore" / "transactions.xlsx"
            ),
            "customers": pd.read_csv(
                RAW_DIR / "singapore" / "client_master.csv"
            ),
            "suppliers": pd.read_excel(
                RAW_DIR / "singapore" / "vendor_master.xlsx"
            ),
            "finance": pd.read_csv(
                RAW_DIR / "singapore" / "finance_extract.csv"
            ),
        },
        "ID": {
            "bookings": pd.read_csv(
                RAW_DIR / "indonesia" / "booking_export.csv"
            ),
            "customers": pd.read_excel(
                RAW_DIR / "indonesia" / "accounts.xlsx"
            ),
            "suppliers": pd.read_csv(
                RAW_DIR / "indonesia" / "supplier_export.csv"
            ),
            "finance": pd.read_csv(
                RAW_DIR / "indonesia" / "finance_id.csv"
            ),
        },
    }


def standard_column_map(country_code: str) -> dict[str, str]:
    if country_code == "MY":
        return {
            "booking_id": "booking_id",
            "booking_date": "booking_date",
            "travel_date": "travel_date",
            "customer_id": "customer_id",
            "supplier_id": "supplier_id",
            "product_type": "product_type",
            "booking_channel": "booking_channel",
            "currency": "currency",
            "booking_value": "booking_value",
            "revenue": "revenue",
            "cost": "cost",
            "booking_status": "booking_status",
        }

    if country_code == "SG":
        return {
            "transaction_ref": "booking_id",
            "txn_date": "booking_date",
            "departure_date": "travel_date",
            "client_code": "customer_id",
            "vendor_code": "supplier_id",
            "service_category": "product_type",
            "booking_method": "booking_channel",
            "txn_currency": "currency",
            "gross_sales": "booking_value",
            "net_revenue": "revenue",
            "direct_cost": "cost",
            "status": "booking_status",
        }

    if country_code == "ID":
        return {
            "booking_no": "booking_id",
            "created_at": "booking_date",
            "journey_date": "travel_date",
            "account_no": "customer_id",
            "provider_code": "supplier_id",
            "travel_product": "product_type",
            "channel": "booking_channel",
            "currency_code": "currency",
            "total_booking_amount": "booking_value",
            "service_revenue": "revenue",
            "supplier_cost": "cost",
            "booking_state": "booking_status",
        }

    raise ValueError(
        f"Unsupported country code: {country_code}"
    )


def standardize_for_profiling(
    df: pd.DataFrame,
    country_code: str,
) -> pd.DataFrame:
    return df.rename(
        columns=standard_column_map(country_code)
    ).copy()


def customer_key(
    country_code: str,
) -> str:
    return {
        "MY": "customer_id",
        "SG": "client_code",
        "ID": "account_no",
    }[country_code]


def supplier_key(
    country_code: str,
) -> str:
    return {
        "MY": "supplier_id",
        "SG": "vendor_code",
        "ID": "provider_code",
    }[country_code]


def profile_basic(
    country_code: str,
    dataset_name: str,
    df: pd.DataFrame,
) -> dict:
    return {
        "country_code": country_code,
        "dataset": dataset_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
    }


def profile_columns(
    country_code: str,
    dataset_name: str,
    df: pd.DataFrame,
) -> pd.DataFrame:
    records = []

    for column in df.columns:
        series = df[column]

        records.append(
            {
                "country_code": country_code,
                "dataset": dataset_name,
                "column_name": column,
                "dtype": str(series.dtype),
                "row_count": len(series),
                "null_count": int(
                    series.isna().sum()
                ),
                "null_pct": round(
                    series.isna().mean() * 100,
                    4,
                ),
                "distinct_count": int(
                    series.nunique(
                        dropna=True
                    )
                ),
            }
        )

    return pd.DataFrame(records)


def booking_quality_checks(
    country_code: str,
    booking_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    supplier_df: pd.DataFrame,
) -> dict:
    df = standardize_for_profiling(
        booking_df,
        country_code,
    )

    booking_date = pd.to_datetime(
        df["booking_date"],
        errors="coerce",
    )

    travel_date = pd.to_datetime(
        df["travel_date"],
        errors="coerce",
    )

    customer_master_key = customer_key(
        country_code
    )

    supplier_master_key = supplier_key(
        country_code
    )

    valid_customers = set(
        customer_df[
            customer_master_key
        ]
        .dropna()
        .astype(str)
    )

    valid_suppliers = set(
        supplier_df[
            supplier_master_key
        ]
        .dropna()
        .astype(str)
    )

    booking_customers = (
        df["customer_id"]
        .dropna()
        .astype(str)
    )

    booking_suppliers = (
        df["supplier_id"]
        .dropna()
        .astype(str)
    )

    expected_currency = {
        "MY": "MYR",
        "SG": "SGD",
        "ID": "IDR",
    }[country_code]

    return {
        "country_code": country_code,
        "row_count": len(df),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "duplicate_booking_ids": int(
            df["booking_id"]
            .duplicated(
                keep=False
            )
            .sum()
        ),
        "missing_booking_id": int(
            df["booking_id"].isna().sum()
        ),
        "missing_customer_id": int(
            df["customer_id"].isna().sum()
        ),
        "missing_supplier_id": int(
            df["supplier_id"].isna().sum()
        ),
        "orphan_customer_refs": int(
            (~booking_customers.isin(
                valid_customers
            )).sum()
        ),
        "orphan_supplier_refs": int(
            (~booking_suppliers.isin(
                valid_suppliers
            )).sum()
        ),
        "invalid_currency": int(
            (
                df["currency"].astype(str)
                != expected_currency
            ).sum()
        ),
        "negative_booking_value": int(
            (
                pd.to_numeric(
                    df["booking_value"],
                    errors="coerce",
                )
                < 0
            ).sum()
        ),
        "travel_before_booking": int(
            (
                travel_date
                < booking_date
            ).sum()
        ),
        "invalid_booking_status": int(
            (
                ~df["booking_status"].isin(
                    [
                        "Confirmed",
                        "Cancelled",
                        "Refunded",
                    ]
                )
            ).sum()
        ),
        "min_booking_date": (
            booking_date.min()
        ),
        "max_booking_date": (
            booking_date.max()
        ),
        "min_travel_date": (
            travel_date.min()
        ),
        "max_travel_date": (
            travel_date.max()
        ),
    }


def value_frequency_profile(
    country_code: str,
    booking_df: pd.DataFrame,
) -> pd.DataFrame:
    df = standardize_for_profiling(
        booking_df,
        country_code,
    )

    columns = [
        "product_type",
        "booking_channel",
        "currency",
        "booking_status",
    ]

    frames = []

    for column in columns:
        counts = (
            df[column]
            .fillna("<NULL>")
            .value_counts(
                dropna=False
            )
            .rename_axis("value")
            .reset_index(name="record_count")
        )

        counts.insert(
            0,
            "field_name",
            column,
        )

        counts.insert(
            0,
            "country_code",
            country_code,
        )

        frames.append(counts)

    return pd.concat(
        frames,
        ignore_index=True,
    )


def numeric_profile(
    country_code: str,
    booking_df: pd.DataFrame,
) -> pd.DataFrame:
    df = standardize_for_profiling(
        booking_df,
        country_code,
    )

    fields = [
        "booking_value",
        "revenue",
        "cost",
    ]

    records = []

    for field in fields:
        values = pd.to_numeric(
            df[field],
            errors="coerce",
        )

        records.append(
            {
                "country_code": country_code,
                "field_name": field,
                "count": int(
                    values.count()
                ),
                "null_or_invalid_count": int(
                    values.isna().sum()
                ),
                "min": values.min(),
                "max": values.max(),
                "mean": values.mean(),
                "median": values.median(),
            }
        )

    return pd.DataFrame(records)


def compare_with_defect_manifest(
    quality_df: pd.DataFrame,
) -> pd.DataFrame:
    manifest_path = (
        REFERENCE_DIR
        / "defect_manifest.csv"
    )

    if not manifest_path.exists():
        return pd.DataFrame()

    manifest = pd.read_csv(
        manifest_path
    )

    mapping = {
        "missing_customer_id":
            "missing_customer_id",
        "missing_supplier_id":
            "missing_supplier_id",
        "orphan_customer":
            "orphan_customer_refs",
        "orphan_supplier":
            "orphan_supplier_refs",
        "unexpected_negative_booking_value":
            "negative_booking_value",
        "invalid_currency":
            "invalid_currency",
        "travel_before_booking":
            "travel_before_booking",
        "invalid_booking_status":
            "invalid_booking_status",
        "duplicate_transaction":
            "duplicate_rows",
    }

    records = []

    for _, row in manifest.iterrows():
        defect_type = row[
            "defect_type"
        ]

        metric_name = mapping.get(
            defect_type
        )

        if metric_name is None:
            continue

        country = row[
            "country_code"
        ]

        country_quality = quality_df.loc[
            quality_df[
                "country_code"
            ] == country
        ]

        if country_quality.empty:
            continue

        detected_count = int(
            country_quality.iloc[0][
                metric_name
            ]
        )

        injected_count = int(
            row[
                "injected_count"
            ]
        )

        records.append(
            {
                "country_code": country,
                "defect_type": defect_type,
                "injected_count":
                    injected_count,
                "detected_count":
                    detected_count,
                "difference":
                    detected_count
                    - injected_count,
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    country_data = (
        load_country_data()
    )

    dataset_summary = []
    column_profiles = []
    booking_quality = []
    value_profiles = []
    numeric_profiles = []

    for country_code, datasets in (
        country_data.items()
    ):
        print(
            f"\nProfiling {country_code}..."
        )

        for dataset_name, df in (
            datasets.items()
        ):
            dataset_summary.append(
                profile_basic(
                    country_code,
                    dataset_name,
                    df,
                )
            )

            column_profiles.append(
                profile_columns(
                    country_code,
                    dataset_name,
                    df,
                )
            )

        quality = booking_quality_checks(
            country_code,
            datasets["bookings"],
            datasets["customers"],
            datasets["suppliers"],
        )

        booking_quality.append(
            quality
        )

        value_profiles.append(
            value_frequency_profile(
                country_code,
                datasets["bookings"],
            )
        )

        numeric_profiles.append(
            numeric_profile(
                country_code,
                datasets["bookings"],
            )
        )

    summary_df = pd.DataFrame(
        dataset_summary
    )

    columns_df = pd.concat(
        column_profiles,
        ignore_index=True,
    )

    quality_df = pd.DataFrame(
        booking_quality
    )

    values_df = pd.concat(
        value_profiles,
        ignore_index=True,
    )

    numeric_df = pd.concat(
        numeric_profiles,
        ignore_index=True,
    )

    detection_df = (
        compare_with_defect_manifest(
            quality_df
        )
    )

    summary_df.to_csv(
        OUTPUT_DIR
        / "dataset_summary.csv",
        index=False,
    )

    columns_df.to_csv(
        OUTPUT_DIR
        / "column_profile.csv",
        index=False,
    )

    quality_df.to_csv(
        OUTPUT_DIR
        / "booking_quality_summary.csv",
        index=False,
    )

    values_df.to_csv(
        OUTPUT_DIR
        / "categorical_value_profile.csv",
        index=False,
    )

    numeric_df.to_csv(
        OUTPUT_DIR
        / "numeric_profile.csv",
        index=False,
    )

    if not detection_df.empty:
        detection_df.to_csv(
            OUTPUT_DIR
            / "defect_detection_comparison.csv",
            index=False,
        )

    print(
        "\nRaw profiling completed."
    )

    print(
        f"Outputs written to: "
        f"{OUTPUT_DIR.relative_to(PROJECT_ROOT)}"
    )

    print(
        "\nBooking quality summary:"
    )

    print(
        quality_df.to_string(
            index=False
        )
    )

    if not detection_df.empty:
        print(
            "\nInjected vs detected defects:"
        )

        print(
            detection_df.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()