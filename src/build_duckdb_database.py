from __future__ import annotations

from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "regional_travel.duckdb"

SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "finance_reconciliation"


def q(path: Path) -> str:
    """
    Convert a Windows path into a SQL-safe forward-slash path.
    """
    return path.resolve().as_posix()


def validate_required_files() -> None:

    required_files = [
        SILVER_DIR / "bookings_clean.parquet",
        SILVER_DIR / "dim_customer_master.parquet",
        SILVER_DIR / "dim_supplier_master.parquet",
        REFERENCE_DIR / "customer_crosswalk.csv",
        REFERENCE_DIR / "supplier_crosswalk.csv",
        REFERENCE_DIR / "product_mapping.csv",
        REFERENCE_DIR / "channel_mapping.csv",
        REFERENCE_DIR / "currency_reference.csv",
        OUTPUT_DIR / "monthly_finance_reconciliation.parquet",
    ]

    missing = [
        str(path.relative_to(PROJECT_ROOT))
        for path in required_files
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Required files are missing:\n"
            + "\n".join(missing)
        )


def create_schemas(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        """
        CREATE SCHEMA IF NOT EXISTS staging;
        CREATE SCHEMA IF NOT EXISTS master;
        CREATE SCHEMA IF NOT EXISTS reference;
        CREATE SCHEMA IF NOT EXISTS control;
        """
    )


def load_silver_bookings(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE staging.bookings AS
        SELECT *
        FROM read_parquet(
            '{q(SILVER_DIR / "bookings_clean.parquet")}'
        );
        """
    )


def load_customer_master(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE master.dim_customer_master AS
        SELECT *
        FROM read_parquet(
            '{q(SILVER_DIR / "dim_customer_master.parquet")}'
        );
        """
    )


def load_supplier_master(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE master.dim_supplier_master AS
        SELECT *
        FROM read_parquet(
            '{q(SILVER_DIR / "dim_supplier_master.parquet")}'
        );
        """
    )


def load_crosswalks(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE reference.customer_crosswalk AS
        SELECT *
        FROM read_csv_auto(
            '{q(REFERENCE_DIR / "customer_crosswalk.csv")}',
            HEADER = TRUE
        );
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE reference.supplier_crosswalk AS
        SELECT *
        FROM read_csv_auto(
            '{q(REFERENCE_DIR / "supplier_crosswalk.csv")}',
            HEADER = TRUE
        );
        """
    )


def load_reference_mappings(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE reference.product_mapping AS
        SELECT *
        FROM read_csv_auto(
            '{q(REFERENCE_DIR / "product_mapping.csv")}',
            HEADER = TRUE
        );
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE reference.channel_mapping AS
        SELECT *
        FROM read_csv_auto(
            '{q(REFERENCE_DIR / "channel_mapping.csv")}',
            HEADER = TRUE
        );
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE reference.currency_reference AS
        SELECT *
        FROM read_csv_auto(
            '{q(REFERENCE_DIR / "currency_reference.csv")}',
            HEADER = TRUE
        );
        """
    )


def load_finance_reconciliation(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        f"""
        CREATE OR REPLACE TABLE control.finance_reconciliation AS
        SELECT *
        FROM read_parquet(
            '{q(OUTPUT_DIR / "monthly_finance_reconciliation.parquet")}'
        );
        """
    )


def create_metadata_table(
    con: duckdb.DuckDBPyConnection,
) -> None:

    con.execute(
        """
        CREATE OR REPLACE TABLE control.pipeline_metadata AS

        SELECT
            current_timestamp AS database_built_at,
            'Regional Travel Performance Analytics'
                AS project_name,
            TRUE AS synthetic_data,
            'MYR' AS reporting_currency,
            'DuckDB' AS database_engine;
        """
    )


def validate_database(
    con: duckdb.DuckDBPyConnection,
) -> None:

    checks = con.execute(
        """
        SELECT
            'staging.bookings' AS object_name,
            COUNT(*) AS row_count
        FROM staging.bookings

        UNION ALL

        SELECT
            'master.dim_customer_master',
            COUNT(*)
        FROM master.dim_customer_master

        UNION ALL

        SELECT
            'master.dim_supplier_master',
            COUNT(*)
        FROM master.dim_supplier_master

        UNION ALL

        SELECT
            'reference.customer_crosswalk',
            COUNT(*)
        FROM reference.customer_crosswalk

        UNION ALL

        SELECT
            'reference.supplier_crosswalk',
            COUNT(*)
        FROM reference.supplier_crosswalk

        UNION ALL

        SELECT
            'reference.product_mapping',
            COUNT(*)
        FROM reference.product_mapping

        UNION ALL

        SELECT
            'reference.channel_mapping',
            COUNT(*)
        FROM reference.channel_mapping

        UNION ALL

        SELECT
            'reference.currency_reference',
            COUNT(*)
        FROM reference.currency_reference

        UNION ALL

        SELECT
            'control.finance_reconciliation',
            COUNT(*)
        FROM control.finance_reconciliation;
        """
    ).fetchdf()

    print(
        "\nDuckDB object row counts"
    )

    print(
        "-------------------------"
    )

    print(
        checks.to_string(
            index=False
        )
    )

    zero_rows = checks.loc[
        checks["row_count"] == 0
    ]

    if not zero_rows.empty:
        raise RuntimeError(
            "One or more DuckDB tables "
            "were created with zero rows."
        )


def print_database_objects(
    con: duckdb.DuckDBPyConnection,
) -> None:

    objects = con.execute(
        """
        SELECT
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema IN (
            'staging',
            'master',
            'reference',
            'control'
        )
        ORDER BY
            table_schema,
            table_name;
        """
    ).fetchdf()

    print(
        "\nDatabase objects"
    )

    print(
        "----------------"
    )

    print(
        objects.to_string(
            index=False
        )
    )


def main() -> None:

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validate_required_files()

    con = duckdb.connect(
        str(
            DATABASE_PATH
        )
    )

    try:

        create_schemas(
            con
        )

        load_silver_bookings(
            con
        )

        load_customer_master(
            con
        )

        load_supplier_master(
            con
        )

        load_crosswalks(
            con
        )

        load_reference_mappings(
            con
        )

        load_finance_reconciliation(
            con
        )

        create_metadata_table(
            con
        )

        validate_database(
            con
        )

        print_database_objects(
            con
        )

    finally:

        con.close()

    print(
        "\nDuckDB database created successfully."
    )

    print(
        "Database:"
    )

    print(
        DATABASE_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()