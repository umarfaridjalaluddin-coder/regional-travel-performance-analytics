from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "data_quality"


def load_rules() -> pd.DataFrame:
    return pd.read_csv(
        CONFIG_DIR / "data_quality_rules.csv"
    )


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
        },
    }


def standard_column_map(country_code: str) -> dict[str, str]:
    mappings = {
        "MY": {
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
        },
        "SG": {
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
        },
        "ID": {
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
        },
    }

    return mappings[country_code]


def standardize_bookings(
    df: pd.DataFrame,
    country_code: str,
) -> pd.DataFrame:
    return df.rename(
        columns=standard_column_map(country_code)
    ).copy()


def customer_key(country_code: str) -> str:
    return {
        "MY": "customer_id",
        "SG": "client_code",
        "ID": "account_no",
    }[country_code]


def supplier_key(country_code: str) -> str:
    return {
        "MY": "supplier_id",
        "SG": "vendor_code",
        "ID": "provider_code",
    }[country_code]


def expected_currency(country_code: str) -> str:
    return {
        "MY": "MYR",
        "SG": "SGD",
        "ID": "IDR",
    }[country_code]


def load_product_mapping() -> pd.DataFrame:
    return pd.read_csv(
        REFERENCE_DIR / "product_mapping.csv"
    )


def load_channel_mapping() -> pd.DataFrame:
    return pd.read_csv(
        REFERENCE_DIR / "channel_mapping.csv"
    )


def evaluate_rule(
    fail_count: int,
    total_count: int,
    threshold_type: str,
    threshold_value: float,
) -> tuple[str, float]:
    fail_pct = (
        fail_count / total_count * 100
        if total_count > 0
        else 0.0
    )

    if threshold_type == "max_fail_count":
        passed = fail_count <= threshold_value

    elif threshold_type == "max_fail_pct":
        passed = fail_pct <= threshold_value

    else:
        raise ValueError(
            f"Unknown threshold type: {threshold_type}"
        )

    return (
        "PASS" if passed else "FAIL",
        round(fail_pct, 4),
    )


def run_country_checks(
    country_code: str,
    datasets: dict[str, pd.DataFrame],
    rules: pd.DataFrame,
    product_mapping: pd.DataFrame,
    channel_mapping: pd.DataFrame,
) -> pd.DataFrame:
    bookings = standardize_bookings(
        datasets["bookings"],
        country_code,
    )

    customers = datasets["customers"]
    suppliers = datasets["suppliers"]

    booking_date = pd.to_datetime(
        bookings["booking_date"],
        errors="coerce",
    )

    travel_date = pd.to_datetime(
        bookings["travel_date"],
        errors="coerce",
    )

    valid_customers = set(
        customers[
            customer_key(country_code)
        ]
        .dropna()
        .astype(str)
    )

    valid_suppliers = set(
        suppliers[
            supplier_key(country_code)
        ]
        .dropna()
        .astype(str)
    )

    allowed_products = set(
        product_mapping.loc[
            product_mapping["country_code"]
            == country_code,
            "source_product",
        ].astype(str)
    )

    allowed_channels = set(
        channel_mapping.loc[
            channel_mapping["country_code"]
            == country_code,
            "source_channel",
        ].astype(str)
    )

    fail_counts = {
        "DQ_BOOKING_001":
            int(bookings["booking_id"].isna().sum()),

        "DQ_BOOKING_002":
            int(
                bookings["booking_id"]
                .duplicated(
                    keep=False
                )
                .sum()
            ),

        "DQ_BOOKING_003":
            int(bookings["customer_id"].isna().sum()),

        "DQ_BOOKING_004":
            int(bookings["supplier_id"].isna().sum()),

        "DQ_BOOKING_005":
            int(
                (
                    bookings["customer_id"]
                    .notna()
                    &
                    ~bookings["customer_id"]
                    .astype(str)
                    .isin(valid_customers)
                ).sum()
            ),

        "DQ_BOOKING_006":
            int(
                (
                    bookings["supplier_id"]
                    .notna()
                    &
                    ~bookings["supplier_id"]
                    .astype(str)
                    .isin(valid_suppliers)
                ).sum()
            ),

        "DQ_BOOKING_007":
            int(
                (
                    bookings["currency"].astype(str)
                    != expected_currency(country_code)
                ).sum()
            ),

        "DQ_BOOKING_008":
            int(
                (
                    pd.to_numeric(
                        bookings["booking_value"],
                        errors="coerce",
                    )
                    < 0
                ).sum()
            ),

        "DQ_BOOKING_009":
            int(
                (
                    travel_date
                    < booking_date
                ).sum()
            ),

        "DQ_BOOKING_010":
            int(
                (
                    ~bookings["booking_status"].isin(
                        [
                            "Confirmed",
                            "Cancelled",
                            "Refunded",
                        ]
                    )
                ).sum()
            ),

        "DQ_BOOKING_011":
            int(
                (
                    bookings["product_type"]
                    .notna()
                    &
                    ~bookings["product_type"]
                    .astype(str)
                    .isin(allowed_products)
                ).sum()
            ),

        "DQ_BOOKING_012":
            int(
                (
                    bookings["booking_channel"]
                    .notna()
                    &
                    ~bookings["booking_channel"]
                    .astype(str)
                    .isin(allowed_channels)
                ).sum()
            ),
    }

    records = []

    total_count = len(bookings)

    for _, rule in rules.iterrows():
        rule_id = rule["rule_id"]

        if rule_id not in fail_counts:
            continue

        fail_count = fail_counts[rule_id]

        status, fail_pct = evaluate_rule(
            fail_count=fail_count,
            total_count=total_count,
            threshold_type=rule[
                "threshold_type"
            ],
            threshold_value=float(
                rule["threshold_value"]
            ),
        )

        records.append(
            {
                "country_code": country_code,
                "rule_id": rule_id,
                "domain": rule["domain"],
                "field_name": rule["field_name"],
                "rule_type": rule["rule_type"],
                "severity": rule["severity"],
                "description": rule["description"],
                "total_records": total_count,
                "failed_records": fail_count,
                "failure_pct": fail_pct,
                "threshold_type":
                    rule["threshold_type"],
                "threshold_value":
                    rule["threshold_value"],
                "status": status,
            }
        )

    return pd.DataFrame(records)


def build_country_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        results.groupby(
            "country_code",
            as_index=False,
        )
        .agg(
            total_rules=("rule_id", "count"),
            passed_rules=(
                "status",
                lambda x: int((x == "PASS").sum())
            ),
            failed_rules=(
                "status",
                lambda x: int((x == "FAIL").sum())
            ),
            critical_failures=(
                "severity",
                lambda x: 0,
            ),
        )
    )

    critical_counts = (
        results.loc[
            (results["severity"] == "critical")
            &
            (results["status"] == "FAIL")
        ]
        .groupby("country_code")
        .size()
    )

    summary["critical_failures"] = (
        summary["country_code"]
        .map(critical_counts)
        .fillna(0)
        .astype(int)
    )

    return summary


def build_reporting_gate(
    results: pd.DataFrame,
) -> pd.DataFrame:
    records = []

    for country_code, group in results.groupby(
        "country_code"
    ):
        critical_failures = group.loc[
            (group["severity"] == "critical")
            &
            (group["status"] == "FAIL")
        ]

        high_failures = group.loc[
            (group["severity"] == "high")
            &
            (group["status"] == "FAIL")
        ]

        if len(critical_failures) > 0:
            gate_status = "BLOCK"

        elif len(high_failures) > 0:
            gate_status = "REVIEW"

        else:
            gate_status = "PASS"

        records.append(
            {
                "country_code": country_code,
                "critical_failed_rules":
                    len(critical_failures),
                "high_failed_rules":
                    len(high_failures),
                "reporting_gate":
                    gate_status,
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    rules = load_rules()
    country_data = load_country_data()

    product_mapping = (
        load_product_mapping()
    )

    channel_mapping = (
        load_channel_mapping()
    )

    results = []

    for country_code, datasets in (
        country_data.items()
    ):
        print(
            f"Running DQ checks for {country_code}..."
        )

        country_results = run_country_checks(
            country_code,
            datasets,
            rules,
            product_mapping,
            channel_mapping,
        )

        results.append(
            country_results
        )

    results_df = pd.concat(
        results,
        ignore_index=True,
    )

    summary_df = build_country_summary(
        results_df
    )

    gate_df = build_reporting_gate(
        results_df
    )

    results_df.to_csv(
        OUTPUT_DIR
        / "dq_rule_results.csv",
        index=False,
    )

    summary_df.to_csv(
        OUTPUT_DIR
        / "dq_country_summary.csv",
        index=False,
    )

    gate_df.to_csv(
        OUTPUT_DIR
        / "reporting_gate.csv",
        index=False,
    )

    print(
        "\nData-quality validation completed."
    )

    print(
        "\nCountry summary:"
    )

    print(
        summary_df.to_string(
            index=False
        )
    )

    print(
        "\nReporting gate:"
    )

    print(
        gate_df.to_string(
            index=False
        )
    )

    failed = results_df.loc[
        results_df["status"] == "FAIL"
    ]

    print(
        "\nFailed rules:"
    )

    if failed.empty:
        print("None")

    else:
        print(
            failed[
                [
                    "country_code",
                    "rule_id",
                    "severity",
                    "failed_records",
                    "failure_pct",
                ]
            ].to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()