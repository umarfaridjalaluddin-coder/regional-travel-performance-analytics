from __future__ import annotations

from pathlib import Path

import duckdb


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "regional_travel.duckdb"
)

SQL_INTERMEDIATE_DIR = (
    PROJECT_ROOT
    / "sql"
    / "intermediate"
)

SQL_MARTS_DIR = (
    PROJECT_ROOT
    / "sql"
    / "marts"
)

GOLD_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "gold"
)


# ============================================================
# SQL FILE EXECUTION ORDER
# ============================================================

INTERMEDIATE_SQL_FILES = [
    "int_bookings_enriched.sql",
    "int_booking_fx.sql",
]

MART_SQL_FILES = [
    "dim_date.sql",
    "dim_country.sql",
    "dim_customer.sql",
    "dim_supplier.sql",
    "dim_product.sql",
    "dim_channel.sql",
    "fact_booking.sql",
    "fact_finance_reconciliation.sql",
]

GOLD_TABLES = [
    "dim_date",
    "dim_country",
    "dim_customer",
    "dim_supplier",
    "dim_product",
    "dim_channel",
    "fact_booking",
    "fact_finance_reconciliation",
]


# ============================================================
# HELPER: EXECUTE SQL FILE
# ============================================================


def execute_sql_file(
    connection: duckdb.DuckDBPyConnection,
    path: Path,
) -> None:

    if not path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {path}"
        )

    print(
        f"Executing: "
        f"{path.relative_to(PROJECT_ROOT)}"
    )

    sql = path.read_text(
        encoding="utf-8"
    )

    connection.execute(
        sql
    )


# ============================================================
# HELPER: EXPORT GOLD TABLE
# ============================================================


def export_gold_table(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> None:

    GOLD_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    parquet_path = (
        GOLD_OUTPUT_DIR
        / f"{table_name}.parquet"
    )

    csv_path = (
        GOLD_OUTPUT_DIR
        / f"{table_name}.csv"
    )

    print(
        f"Exporting gold.{table_name}"
    )

    connection.execute(
        f"""
        COPY (
            SELECT *
            FROM gold.{table_name}
        )
        TO '{parquet_path.as_posix()}'
        (
            FORMAT PARQUET,
            COMPRESSION ZSTD
        );
        """
    )

    connection.execute(
        f"""
        COPY (
            SELECT *
            FROM gold.{table_name}
        )
        TO '{csv_path.as_posix()}'
        (
            HEADER,
            DELIMITER ','
        );
        """
    )


# ============================================================
# VALIDATION: GOLD ROW COUNTS
# ============================================================


def print_row_counts(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "Gold table row counts"
    )

    print(
        "---------------------"
    )

    for table_name in GOLD_TABLES:

        row_count = (
            connection.execute(
                f"""
                SELECT COUNT(*)
                FROM gold.{table_name}
                """
            )
            .fetchone()[0]
        )

        print(
            f"{table_name}: "
            f"{row_count:,}"
        )


# ============================================================
# VALIDATION: FACT BOOKING
# ============================================================


def validate_fact_booking(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "Fact booking validation"
    )

    print(
        "-----------------------"
    )

    country_summary = (
        connection.execute(
            """
            SELECT
                country_code,

                COUNT(*) AS row_count,

                ROUND(
                    SUM(
                        booking_value_reporting
                    ),
                    2
                ) AS booking_value_reporting,

                ROUND(
                    SUM(
                        revenue_reporting
                    ),
                    2
                ) AS revenue_reporting,

                ROUND(
                    SUM(
                        cost_reporting
                    ),
                    2
                ) AS cost_reporting,

                ROUND(
                    SUM(
                        gross_margin_reporting
                    ),
                    2
                ) AS gross_margin_reporting

            FROM gold.fact_booking

            GROUP BY
                country_code

            ORDER BY
                country_code
            """
        )
        .fetchdf()
    )

    print(
        country_summary.to_string(
            index=False
        )
    )

    missing_fx = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM gold.fact_booking
            WHERE rate_to_reporting_currency
                IS NULL
            """
        )
        .fetchone()[0]
    )

    missing_customers = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM gold.fact_booking
            WHERE regional_customer_id
                IS NULL
            """
        )
        .fetchone()[0]
    )

    missing_suppliers = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM gold.fact_booking
            WHERE regional_supplier_id
                IS NULL
            """
        )
        .fetchone()[0]
    )

    duplicate_booking_ids = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    booking_id
                FROM gold.fact_booking
                GROUP BY booking_id
                HAVING COUNT(*) > 1
            )
            """
        )
        .fetchone()[0]
    )

    print()
    print(
        f"Missing FX rates: "
        f"{missing_fx:,}"
    )

    print(
        f"Missing regional customers: "
        f"{missing_customers:,}"
    )

    print(
        f"Missing regional suppliers: "
        f"{missing_suppliers:,}"
    )

    print(
        f"Duplicate booking IDs: "
        f"{duplicate_booking_ids:,}"
    )

    if missing_fx != 0:
        raise RuntimeError(
            (
                "Gold validation failed: "
                "missing FX rates detected."
            )
        )

    if missing_customers != 0:
        raise RuntimeError(
            (
                "Gold validation failed: "
                "missing regional customer "
                "IDs detected."
            )
        )

    if missing_suppliers != 0:
        raise RuntimeError(
            (
                "Gold validation failed: "
                "missing regional supplier "
                "IDs detected."
            )
        )

    if duplicate_booking_ids != 0:
        raise RuntimeError(
            (
                "Gold validation failed: "
                "duplicate booking IDs "
                "detected."
            )
        )


# ============================================================
# VALIDATION: FX COVERAGE BY COUNTRY
# ============================================================


def validate_fx_coverage(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "FX coverage"
    )

    print(
        "-----------"
    )

    fx_summary = (
        connection.execute(
            """
            SELECT
                country_code,

                transaction_currency,

                COUNT(*) AS booking_rows,

                COUNT(
                    rate_to_reporting_currency
                ) AS rows_with_fx,

                COUNT(*) -
                COUNT(
                    rate_to_reporting_currency
                ) AS rows_missing_fx

            FROM gold.fact_booking

            GROUP BY
                country_code,
                transaction_currency

            ORDER BY
                country_code,
                transaction_currency
            """
        )
        .fetchdf()
    )

    print(
        fx_summary.to_string(
            index=False
        )
    )


# ============================================================
# VALIDATION: DIMENSION COUNTS
# ============================================================


def validate_dimensions(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "Dimension validation"
    )

    print(
        "--------------------"
    )

    customer_duplicates = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    regional_customer_id
                FROM gold.dim_customer
                GROUP BY
                    regional_customer_id
                HAVING COUNT(*) > 1
            )
            """
        )
        .fetchone()[0]
    )

    supplier_duplicates = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    regional_supplier_id
                FROM gold.dim_supplier
                GROUP BY
                    regional_supplier_id
                HAVING COUNT(*) > 1
            )
            """
        )
        .fetchone()[0]
    )

    product_duplicates = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    regional_product
                FROM gold.dim_product
                GROUP BY
                    regional_product
                HAVING COUNT(*) > 1
            )
            """
        )
        .fetchone()[0]
    )

    channel_duplicates = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    regional_channel
                FROM gold.dim_channel
                GROUP BY
                    regional_channel
                HAVING COUNT(*) > 1
            )
            """
        )
        .fetchone()[0]
    )

    print(
        f"Duplicate customer dimension keys: "
        f"{customer_duplicates:,}"
    )

    print(
        f"Duplicate supplier dimension keys: "
        f"{supplier_duplicates:,}"
    )

    print(
        f"Duplicate product values: "
        f"{product_duplicates:,}"
    )

    print(
        f"Duplicate channel values: "
        f"{channel_duplicates:,}"
    )

    if customer_duplicates != 0:
        raise RuntimeError(
            (
                "Dimension validation failed: "
                "duplicate customer keys."
            )
        )

    if supplier_duplicates != 0:
        raise RuntimeError(
            (
                "Dimension validation failed: "
                "duplicate supplier keys."
            )
        )

    if product_duplicates != 0:
        raise RuntimeError(
            (
                "Dimension validation failed: "
                "duplicate products."
            )
        )

    if channel_duplicates != 0:
        raise RuntimeError(
            (
                "Dimension validation failed: "
                "duplicate channels."
            )
        )


# ============================================================
# VALIDATION: FINANCE RECONCILIATION
# ============================================================


def validate_finance_fact(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "Finance reconciliation coverage"
    )

    print(
        "-------------------------------"
    )

    finance_summary = (
        connection.execute(
            """
            SELECT
                source_country,

                COUNT(*) AS month_count,

                SUM(
                    CASE
                        WHEN reconciliation_status = 'PASS'
                        THEN 1
                        ELSE 0
                    END
                ) AS pass_months,

                SUM(
                    CASE
                        WHEN reconciliation_status = 'REVIEW'
                        THEN 1
                        ELSE 0
                    END
                ) AS review_months,

                SUM(
                    CASE
                        WHEN reconciliation_status = 'FAIL'
                        THEN 1
                        ELSE 0
                    END
                ) AS fail_months

            FROM gold.fact_finance_reconciliation

            GROUP BY
                source_country

            ORDER BY
                source_country
            """
        )
        .fetchdf()
    )

    print(
        finance_summary.to_string(
            index=False
        )
    )

    finance_month_count = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM gold.fact_finance_reconciliation
            """
        )
        .fetchone()[0]
    )

    if finance_month_count != 72:
        raise RuntimeError(
            (
                "Expected 72 finance "
                "reconciliation rows, "
                f"found {finance_month_count}."
            )
        )


# ============================================================
# VALIDATION: STAR SCHEMA SUMMARY
# ============================================================


def print_star_schema_summary(
    connection: duckdb.DuckDBPyConnection,
) -> None:

    print()
    print(
        "Star schema summary"
    )

    print(
        "-------------------"
    )

    summary = (
        connection.execute(
            """
            SELECT
                'Fact Booking' AS object_name,
                COUNT(*) AS row_count
            FROM gold.fact_booking

            UNION ALL

            SELECT
                'Fact Finance Reconciliation',
                COUNT(*)
            FROM gold.fact_finance_reconciliation

            UNION ALL

            SELECT
                'Dim Customer',
                COUNT(*)
            FROM gold.dim_customer

            UNION ALL

            SELECT
                'Dim Supplier',
                COUNT(*)
            FROM gold.dim_supplier

            UNION ALL

            SELECT
                'Dim Product',
                COUNT(*)
            FROM gold.dim_product

            UNION ALL

            SELECT
                'Dim Channel',
                COUNT(*)
            FROM gold.dim_channel

            UNION ALL

            SELECT
                'Dim Country',
                COUNT(*)
            FROM gold.dim_country

            UNION ALL

            SELECT
                'Dim Date',
                COUNT(*)
            FROM gold.dim_date
            """
        )
        .fetchdf()
    )

    print(
        summary.to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print(
        "Building Stage 16 Gold layer..."
    )

    print()

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            (
                "DuckDB database not found: "
                f"{DATABASE_PATH}"
            )
        )

    GOLD_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = duckdb.connect(
        str(
            DATABASE_PATH
        )
    )

    try:

        # ====================================================
        # CREATE REQUIRED SCHEMAS
        # ====================================================

        connection.execute(
            """
            CREATE SCHEMA IF NOT EXISTS
                intermediate;
            """
        )

        connection.execute(
            """
            CREATE SCHEMA IF NOT EXISTS
                gold;
            """
        )

        # ====================================================
        # INTERMEDIATE TRANSFORMATIONS
        # ====================================================

        print(
            "Building intermediate layer..."
        )

        print(
            "------------------------------"
        )

        for file_name in (
            INTERMEDIATE_SQL_FILES
        ):

            execute_sql_file(
                connection,
                SQL_INTERMEDIATE_DIR
                / file_name,
            )

        print()

        # ====================================================
        # GOLD / STAR SCHEMA
        # ====================================================

        print(
            "Building Gold star schema..."
        )

        print(
            "----------------------------"
        )

        for file_name in (
            MART_SQL_FILES
        ):

            execute_sql_file(
                connection,
                SQL_MARTS_DIR
                / file_name,
            )

        # ====================================================
        # VALIDATION
        # ====================================================

        print_row_counts(
            connection
        )

        validate_fact_booking(
            connection
        )

        validate_fx_coverage(
            connection
        )

        validate_dimensions(
            connection
        )

        validate_finance_fact(
            connection
        )

        print_star_schema_summary(
            connection
        )

        # ====================================================
        # EXPORT FILES
        # ====================================================

        print()
        print(
            "Exporting Gold tables..."
        )

        print(
            "-----------------------"
        )

        for table_name in (
            GOLD_TABLES
        ):

            export_gold_table(
                connection,
                table_name,
            )

        print()
        print(
            "Stage 16 Gold layer completed successfully."
        )

        print()

        print(
            "Gold files written to:"
        )

        print(
            GOLD_OUTPUT_DIR.relative_to(
                PROJECT_ROOT
            )
        )

        print()

        print(
            "Power BI recommended source:"
        )

        print(
            "data/gold/*.parquet"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()