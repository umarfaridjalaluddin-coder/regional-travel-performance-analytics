from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

SILVER_DIR = (
    PROJECT_ROOT
    / "data"
    / "silver"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "finance_reconciliation"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "finance_reconciliation_config.json"
)


def load_config() -> dict:
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_silver_bookings() -> pd.DataFrame:

    path = (
        SILVER_DIR
        / "bookings_clean.parquet"
    )

    if not path.exists():
        raise FileNotFoundError(
            "Silver bookings not found. "
            "Run build_silver_bookings.py first."
        )

    df = pd.read_parquet(
        path
    )

    df["booking_date"] = (
        pd.to_datetime(
            df["booking_date"],
            errors="coerce",
        )
    )

    return df


def load_my_finance() -> pd.DataFrame:

    df = pd.read_csv(
        RAW_DIR
        / "malaysia"
        / "finance.csv"
    )

    df = df.rename(
        columns={
            "finance_month":
                "finance_month",
            "country":
                "source_country",
            "revenue":
                "finance_revenue_local",
            "cost":
                "finance_cost_local",
            "gross_margin":
                "finance_gross_margin_local",
            "transaction_count":
                "finance_transactions",
        }
    )

    return df


def load_sg_finance() -> pd.DataFrame:

    df = pd.read_csv(
        RAW_DIR
        / "singapore"
        / "finance_extract.csv"
    )

    df = df.rename(
        columns={
            "period":
                "finance_month",
            "market":
                "source_country",
            "sales_revenue":
                "finance_revenue_local",
            "operating_cost":
                "finance_cost_local",
            "margin":
                "finance_gross_margin_local",
            "transactions":
                "finance_transactions",
        }
    )

    return df


def load_id_finance() -> pd.DataFrame:

    df = pd.read_csv(
        RAW_DIR
        / "indonesia"
        / "finance_id.csv"
    )

    df = df.rename(
        columns={
            "accounting_period":
                "finance_month",
            "country_code":
                "source_country",
            "reported_revenue":
                "finance_revenue_local",
            "reported_cost":
                "finance_cost_local",
            "reported_margin":
                "finance_gross_margin_local",
            "reported_transactions":
                "finance_transactions",
        }
    )

    return df


def standardize_finance() -> pd.DataFrame:

    frames = [
        load_my_finance(),
        load_sg_finance(),
        load_id_finance(),
    ]

    finance = pd.concat(
        frames,
        ignore_index=True,
    )

    finance["finance_month"] = (
        pd.to_datetime(
            finance["finance_month"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    numeric_columns = [
        "finance_revenue_local",
        "finance_cost_local",
        "finance_gross_margin_local",
        "finance_transactions",
    ]

    for column in numeric_columns:
        finance[column] = (
            pd.to_numeric(
                finance[column],
                errors="coerce",
            )
        )

    finance[
        "finance_transactions"
    ] = finance[
        "finance_transactions"
    ].astype("Int64")

    expected_columns = [
        "finance_month",
        "source_country",
        "finance_revenue_local",
        "finance_cost_local",
        "finance_gross_margin_local",
        "finance_transactions",
    ]

    return finance[
        expected_columns
    ].copy()


def build_booking_monthly(
    bookings: pd.DataFrame,
) -> pd.DataFrame:

    working = bookings.copy()

    working["finance_month"] = (
        working["booking_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        working.groupby(
            [
                "source_country",
                "finance_month",
            ],
            as_index=False,
        )
        .agg(
            booking_revenue_local=(
                "revenue_local",
                "sum",
            ),
            booking_cost_local=(
                "cost_local",
                "sum",
            ),
            booking_gross_margin_local=(
                "gross_margin_local",
                "sum",
            ),
            booking_transactions=(
                "booking_id",
                "count",
            ),
        )
    )

    return monthly


def calculate_variance(
    actual: pd.Series,
    reference: pd.Series,
) -> tuple[
    pd.Series,
    pd.Series,
]:

    absolute_variance = (
        actual
        - reference
    )

    denominator = (
        reference
        .abs()
        .replace(
            0,
            pd.NA,
        )
    )

    variance_pct = (
        absolute_variance
        .abs()
        .div(
            denominator
        )
        * 100
    )

    variance_pct = (
        variance_pct
        .fillna(
            0
        )
    )

    return (
        absolute_variance,
        variance_pct,
    )


def classify_variance(
    variance_pct: float,
    pass_threshold: float,
    review_threshold: float,
) -> str:

    if pd.isna(
        variance_pct
    ):
        return "REVIEW"

    if (
        variance_pct
        <= pass_threshold
    ):
        return "PASS"

    if (
        variance_pct
        <= review_threshold
    ):
        return "REVIEW"

    return "FAIL"


def add_metric_variances(
    df: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:

    result = df.copy()

    metric_map = {
        "revenue": (
            "booking_revenue_local",
            "finance_revenue_local",
        ),
        "cost": (
            "booking_cost_local",
            "finance_cost_local",
        ),
        "gross_margin": (
            "booking_gross_margin_local",
            "finance_gross_margin_local",
        ),
        "transactions": (
            "booking_transactions",
            "finance_transactions",
        ),
    }

    for metric, columns in (
        metric_map.items()
    ):
        (
            booking_column,
            finance_column,
        ) = columns

        (
            absolute_variance,
            variance_pct,
        ) = calculate_variance(
            result[
                booking_column
            ],
            result[
                finance_column
            ],
        )

        result[
            f"{metric}_variance"
        ] = absolute_variance

        result[
            f"{metric}_variance_pct"
        ] = variance_pct.round(
            4
        )

        pass_threshold = float(
            config[
                metric
            ][
                "pass_variance_pct"
            ]
        )

        review_threshold = float(
            config[
                metric
            ][
                "review_variance_pct"
            ]
        )

        result[
            f"{metric}_status"
        ] = result[
            f"{metric}_variance_pct"
        ].apply(
            lambda value:
                classify_variance(
                    value,
                    pass_threshold,
                    review_threshold,
                )
        )

    return result


def overall_status(
    row: pd.Series,
) -> str:

    statuses = [
        row["revenue_status"],
        row["cost_status"],
        row["gross_margin_status"],
        row["transactions_status"],
    ]

    if "FAIL" in statuses:
        return "FAIL"

    if "REVIEW" in statuses:
        return "REVIEW"

    return "PASS"


def add_overall_status(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result[
        "reconciliation_status"
    ] = result.apply(
        overall_status,
        axis=1,
    )

    return result


def add_variance_direction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result[
        "revenue_variance_direction"
    ] = result[
        "revenue_variance"
    ].apply(
        lambda value:
            (
                "BOOKING_ABOVE_FINANCE"
                if value > 0
                else (
                    "BOOKING_BELOW_FINANCE"
                    if value < 0
                    else "MATCH"
                )
            )
    )

    result[
        "cost_variance_direction"
    ] = result[
        "cost_variance"
    ].apply(
        lambda value:
            (
                "BOOKING_ABOVE_FINANCE"
                if value > 0
                else (
                    "BOOKING_BELOW_FINANCE"
                    if value < 0
                    else "MATCH"
                )
            )
    )

    return result


def build_country_summary(
    reconciliation: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        reconciliation.groupby(
            "source_country",
            as_index=False,
        )
        .agg(
            months=(
                "finance_month",
                "nunique",
            ),
            pass_months=(
                "reconciliation_status",
                lambda values:
                    int(
                        (
                            values
                            == "PASS"
                        ).sum()
                    ),
            ),
            review_months=(
                "reconciliation_status",
                lambda values:
                    int(
                        (
                            values
                            == "REVIEW"
                        ).sum()
                    ),
            ),
            fail_months=(
                "reconciliation_status",
                lambda values:
                    int(
                        (
                            values
                            == "FAIL"
                        ).sum()
                    ),
            ),
            total_booking_revenue_local=(
                "booking_revenue_local",
                "sum",
            ),
            total_finance_revenue_local=(
                "finance_revenue_local",
                "sum",
            ),
            total_booking_cost_local=(
                "booking_cost_local",
                "sum",
            ),
            total_finance_cost_local=(
                "finance_cost_local",
                "sum",
            ),
            total_booking_transactions=(
                "booking_transactions",
                "sum",
            ),
            total_finance_transactions=(
                "finance_transactions",
                "sum",
            ),
        )
    )

    summary[
        "revenue_total_variance"
    ] = (
        summary[
            "total_booking_revenue_local"
        ]
        - summary[
            "total_finance_revenue_local"
        ]
    )

    summary[
        "cost_total_variance"
    ] = (
        summary[
            "total_booking_cost_local"
        ]
        - summary[
            "total_finance_cost_local"
        ]
    )

    summary[
        "transaction_total_variance"
    ] = (
        summary[
            "total_booking_transactions"
        ]
        - summary[
            "total_finance_transactions"
        ]
    )

    return summary


def build_exception_report(
    reconciliation: pd.DataFrame,
) -> pd.DataFrame:

    exceptions = (
        reconciliation.loc[
            reconciliation[
                "reconciliation_status"
            ]
            != "PASS"
        ]
        .copy()
    )

    if exceptions.empty:
        return exceptions

    return exceptions.sort_values(
        [
            "reconciliation_status",
            "source_country",
            "finance_month",
        ]
    )


def validate_reconciliation(
    reconciliation: pd.DataFrame,
) -> None:

    duplicate_months = (
        reconciliation
        .duplicated(
            subset=[
                "source_country",
                "finance_month",
            ],
            keep=False,
        )
        .sum()
    )

    if duplicate_months > 0:
        raise RuntimeError(
            "Finance reconciliation "
            "contains duplicate "
            "country-month combinations."
        )

    required_columns = [
        "booking_revenue_local",
        "finance_revenue_local",
        "booking_cost_local",
        "finance_cost_local",
        "booking_transactions",
        "finance_transactions",
    ]

    for column in required_columns:

        missing = (
            reconciliation[
                column
            ]
            .isna()
            .sum()
        )

        if missing > 0:
            raise RuntimeError(
                f"{column} contains "
                f"{missing} missing values."
            )


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    config = load_config()

    bookings = (
        load_silver_bookings()
    )

    finance = (
        standardize_finance()
    )

    booking_monthly = (
        build_booking_monthly(
            bookings
        )
    )

    reconciliation = (
        finance.merge(
            booking_monthly,
            on=[
                "source_country",
                "finance_month",
            ],
            how="outer",
            validate="one_to_one",
            indicator=True,
        )
    )

    unmatched = (
        reconciliation.loc[
            reconciliation[
                "_merge"
            ]
            != "both"
        ]
        .copy()
    )

    if not unmatched.empty:

        print(
            "\nWARNING: unmatched "
            "country-month records detected."
        )

        print(
            unmatched[
                [
                    "source_country",
                    "finance_month",
                    "_merge",
                ]
            ].to_string(
                index=False
            )
        )

    reconciliation = (
        reconciliation.loc[
            reconciliation[
                "_merge"
            ]
            == "both"
        ]
        .drop(
            columns=[
                "_merge"
            ]
        )
        .copy()
    )

    reconciliation = (
        add_metric_variances(
            reconciliation,
            config,
        )
    )

    reconciliation = (
        add_variance_direction(
            reconciliation
        )
    )

    reconciliation = (
        add_overall_status(
            reconciliation
        )
    )

    validate_reconciliation(
        reconciliation
    )

    country_summary = (
        build_country_summary(
            reconciliation
        )
    )

    exceptions = (
        build_exception_report(
            reconciliation
        )
    )

    reconciliation.to_csv(
        OUTPUT_DIR
        / "monthly_finance_reconciliation.csv",
        index=False,
    )

    reconciliation.to_parquet(
        OUTPUT_DIR
        / "monthly_finance_reconciliation.parquet",
        index=False,
    )

    country_summary.to_csv(
        OUTPUT_DIR
        / "finance_reconciliation_country_summary.csv",
        index=False,
    )

    exceptions.to_csv(
        OUTPUT_DIR
        / "finance_reconciliation_exceptions.csv",
        index=False,
    )

    if not unmatched.empty:

        unmatched.to_csv(
            OUTPUT_DIR
            / "unmatched_country_months.csv",
            index=False,
        )

    print(
        "\nFinance reconciliation completed."
    )

    print(
        "\nMonthly reconciliation status:"
    )

    status_summary = (
        reconciliation.groupby(
            [
                "source_country",
                "reconciliation_status",
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
    )

    print(
        status_summary.to_string()
    )

    print(
        "\nCountry summary:"
    )

    print(
        country_summary.to_string(
            index=False
        )
    )

    print(
        "\nLargest revenue variances:"
    )

    largest_variances = (
        reconciliation
        .assign(
            absolute_revenue_variance_pct=
                reconciliation[
                    "revenue_variance_pct"
                ].abs()
        )
        .sort_values(
            "absolute_revenue_variance_pct",
            ascending=False,
        )
        [
            [
                "source_country",
                "finance_month",
                "booking_revenue_local",
                "finance_revenue_local",
                "revenue_variance",
                "revenue_variance_pct",
                "revenue_status",
                "reconciliation_status",
            ]
        ]
        .head(15)
    )

    print(
        largest_variances.to_string(
            index=False
        )
    )

    print(
        "\nOutputs written to:"
    )

    print(
        OUTPUT_DIR.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()