from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd
from faker import Faker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.json"

RAW_DIR = PROJECT_ROOT / "data" / "raw"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"

fake = Faker()
Faker.seed(42)


PRODUCTS = ["Air", "Hotel", "Ground", "Other"]
DESTINATIONS = [
    "MY",
    "SG",
    "ID",
    "TH",
    "JP",
    "AU",
    "GB",
    "US",
    "VN",
    "CN",
]

CUSTOMER_COUNTS = {
    "MY": 320,
    "SG": 220,
    "ID": 260,
}

SUPPLIER_COUNTS = {
    "MY": 80,
    "SG": 60,
    "ID": 70,
}


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def make_customer_master(
    country_code: str,
    count: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    records = []

    segments = ["Enterprise", "Mid-Market", "SME", "Government"]
    industries = [
        "Technology",
        "Financial Services",
        "Manufacturing",
        "Energy",
        "Healthcare",
        "Professional Services",
        "Education",
        "Government",
        "Retail",
        "Logistics",
    ]

    for i in range(1, count + 1):
        customer_id = f"{country_code}-C{i:04d}"

        records.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.company(),
                "segment": rng.choice(
                    segments,
                    p=[0.22, 0.34, 0.30, 0.14],
                ),
                "industry": rng.choice(industries),
                "account_manager": fake.name(),
                "contract_start_date": pd.Timestamp(
                    rng.choice(
                        pd.date_range(
                            "2020-01-01",
                            "2025-12-31",
                            freq="D",
                        )
                    )
                ).date(),
                "contract_end_date": pd.Timestamp(
                    rng.choice(
                        pd.date_range(
                            "2026-09-01",
                            "2029-12-31",
                            freq="D",
                        )
                    )
                ).date(),
                "status": rng.choice(
                    ["Active", "Inactive"],
                    p=[0.94, 0.06],
                ),
            }
        )

    return pd.DataFrame(records)


def make_supplier_master(
    country_code: str,
    count: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    records = []

    supplier_types = ["Air", "Hotel", "Ground", "Other"]

    for i in range(1, count + 1):
        supplier_type = rng.choice(
            supplier_types,
            p=[0.35, 0.35, 0.20, 0.10],
        )

        records.append(
            {
                "supplier_id": f"{country_code}-S{i:04d}",
                "supplier_name": fake.company(),
                "supplier_type": supplier_type,
                "preferred_supplier_flag": rng.choice(
                    ["Y", "N"],
                    p=[0.45, 0.55],
                ),
                "country": country_code,
                "status": rng.choice(
                    ["Active", "Inactive"],
                    p=[0.97, 0.03],
                ),
            }
        )

    return pd.DataFrame(records)


def make_booking_data(
    country_code: str,
    row_count: int,
    customers: pd.DataFrame,
    suppliers: pd.DataFrame,
    config: dict,
    rng: np.random.Generator,
) -> pd.DataFrame:
    start_date = pd.Timestamp(config["start_date"])
    end_date = pd.Timestamp(config["end_date"])

    number_of_days = (end_date - start_date).days + 1

    booking_dates = start_date + pd.to_timedelta(
        rng.integers(0, number_of_days, size=row_count),
        unit="D",
    )

    advance_days = np.maximum(
        0,
        rng.gamma(
            shape=2.2,
            scale=8.0,
            size=row_count,
        ).astype(int),
    )

    travel_dates = booking_dates + pd.to_timedelta(
        advance_days,
        unit="D",
    )

    product_types = rng.choice(
        PRODUCTS,
        size=row_count,
        p=[0.54, 0.29, 0.11, 0.06],
    )

    customer_ids = rng.choice(
        customers["customer_id"].to_numpy(),
        size=row_count,
    )

    supplier_ids = []

    supplier_lookup = {
        product: suppliers.loc[
            suppliers["supplier_type"] == product,
            "supplier_id",
        ].to_numpy()
        for product in PRODUCTS
    }

    all_supplier_ids = suppliers["supplier_id"].to_numpy()

    for product in product_types:
        candidates = supplier_lookup.get(product)

        if candidates is None or len(candidates) == 0:
            candidates = all_supplier_ids

        supplier_ids.append(rng.choice(candidates))

    local_currency = config["countries"][country_code]["local_currency"]

    booking_value = rng.lognormal(
        mean=7.6,
        sigma=0.85,
        size=row_count,
    )

    if country_code == "ID":
        booking_value *= 3500

    elif country_code == "SG":
        booking_value *= 0.75

    revenue_rate = rng.uniform(
        0.06,
        0.16,
        size=row_count,
    )

    base_revenue = booking_value * revenue_rate

    cost_ratio = rng.uniform(
        0.55,
        0.88,
        size=row_count,
    )

    base_cost = base_revenue * cost_ratio

    status = rng.choice(
        ["Confirmed", "Cancelled", "Refunded"],
        size=row_count,
        p=[0.94, 0.04, 0.02],
    )

    revenue = np.where(
        status == "Confirmed",
        base_revenue,
        np.where(
            status == "Refunded",
            -base_revenue,
            0.0,
        ),
    )

    cost = np.where(
        status == "Confirmed",
        base_cost,
        np.where(
            status == "Refunded",
            -base_cost,
            0.0,
        ),
    )

    booking_channel = rng.choice(
        ["Online", "Offline"],
        size=row_count,
        p=[0.58, 0.42],
    )

    dataframe = pd.DataFrame(
        {
            "booking_id": [
                f"{country_code}-B{i:08d}"
                for i in range(1, row_count + 1)
            ],
            "booking_date": booking_dates,
            "travel_date": travel_dates,
            "customer_id": customer_ids,
            "supplier_id": supplier_ids,
            "product_type": product_types,
            "booking_channel": booking_channel,
            "destination_country": rng.choice(
                DESTINATIONS,
                size=row_count,
            ),
            "currency": local_currency,
            "booking_value": np.round(booking_value, 2),
            "revenue": np.round(revenue, 2),
            "cost": np.round(cost, 2),
            "booking_status": status,
            "agent_id": rng.choice(
                [
                    "AG001",
                    "AG002",
                    "AG003",
                    "AG004",
                    "AG005",
                    None,
                ],
                size=row_count,
                p=[
                    0.12,
                    0.12,
                    0.12,
                    0.12,
                    0.12,
                    0.40,
                ],
            ),
        }
    )

    return dataframe


def make_finance_data(
    bookings: pd.DataFrame,
    country_code: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    working = bookings.copy()

    working["finance_month"] = (
        pd.to_datetime(working["booking_date"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    finance = (
        working.groupby(
            "finance_month",
            as_index=False,
        )
        .agg(
            revenue=("revenue", "sum"),
            cost=("cost", "sum"),
            transaction_count=("booking_id", "nunique"),
        )
    )

    finance["gross_margin"] = (
        finance["revenue"] - finance["cost"]
    )

    # Deliberate synthetic finance adjustments.
    revenue_adjustment = rng.normal(
        0.0,
        0.0025,
        size=len(finance),
    )

    cost_adjustment = rng.normal(
        0.0,
        0.0025,
        size=len(finance),
    )

    finance["revenue"] *= 1 + revenue_adjustment
    finance["cost"] *= 1 + cost_adjustment

    finance["gross_margin"] = (
        finance["revenue"] - finance["cost"]
    )

    finance.insert(
        1,
        "country",
        country_code,
    )

    monetary_columns = [
        "revenue",
        "cost",
        "gross_margin",
    ]

    finance[monetary_columns] = finance[
        monetary_columns
    ].round(2)

    return finance


def add_defect(
    manifest: list,
    country: str,
    dataset: str,
    defect_type: str,
    count: int,
    description: str,
) -> None:
    manifest.append(
        {
            "country_code": country,
            "dataset": dataset,
            "defect_type": defect_type,
            "injected_count": count,
            "description": description,
        }
    )


def inject_booking_defects(
    dataframe: pd.DataFrame,
    country_code: str,
    rng: np.random.Generator,
    manifest: list,
) -> pd.DataFrame:
    df = dataframe.copy()

    n = len(df)

    defect_counts = {
        "missing_customer": max(5, int(n * 0.0003)),
        "missing_supplier": max(5, int(n * 0.0003)),
        "orphan_customer": max(5, int(n * 0.0002)),
        "orphan_supplier": max(5, int(n * 0.0002)),
        "negative_value": max(5, int(n * 0.0002)),
        "invalid_currency": max(5, int(n * 0.0002)),
        "bad_travel_date": max(5, int(n * 0.0003)),
        "invalid_status": max(5, int(n * 0.0002)),
        "product_alias": max(10, int(n * 0.0005)),
    }

    available_indices = np.arange(n)
    rng.shuffle(available_indices)

    pointer = 0

    selected = {}

    for defect_name, defect_count in defect_counts.items():
        selected[defect_name] = available_indices[
            pointer : pointer + defect_count
        ]
        pointer += defect_count

    df.loc[
        selected["missing_customer"],
        "customer_id",
    ] = None

    add_defect(
        manifest,
        country_code,
        "booking",
        "missing_customer_id",
        defect_counts["missing_customer"],
        "Customer identifier deliberately set to null.",
    )

    df.loc[
        selected["missing_supplier"],
        "supplier_id",
    ] = None

    add_defect(
        manifest,
        country_code,
        "booking",
        "missing_supplier_id",
        defect_counts["missing_supplier"],
        "Supplier identifier deliberately set to null.",
    )

    df.loc[
        selected["orphan_customer"],
        "customer_id",
    ] = [
        f"{country_code}-UNKNOWN-C{i:04d}"
        for i in range(defect_counts["orphan_customer"])
    ]

    add_defect(
        manifest,
        country_code,
        "booking",
        "orphan_customer",
        defect_counts["orphan_customer"],
        "Booking references customer absent from customer master.",
    )

    df.loc[
        selected["orphan_supplier"],
        "supplier_id",
    ] = [
        f"{country_code}-UNKNOWN-S{i:04d}"
        for i in range(defect_counts["orphan_supplier"])
    ]

    add_defect(
        manifest,
        country_code,
        "booking",
        "orphan_supplier",
        defect_counts["orphan_supplier"],
        "Booking references supplier absent from supplier master.",
    )

    df.loc[
        selected["negative_value"],
        "booking_value",
    ] *= -1

    add_defect(
        manifest,
        country_code,
        "booking",
        "unexpected_negative_booking_value",
        defect_counts["negative_value"],
        "Booking value deliberately changed to negative.",
    )

    df.loc[
        selected["invalid_currency"],
        "currency",
    ] = "XXX"

    add_defect(
        manifest,
        country_code,
        "booking",
        "invalid_currency",
        defect_counts["invalid_currency"],
        "Invalid ISO-style currency code inserted.",
    )

    bad_date_indices = selected["bad_travel_date"]

    df.loc[
        bad_date_indices,
        "travel_date",
    ] = (
        pd.to_datetime(
            df.loc[
                bad_date_indices,
                "booking_date",
            ]
        )
        - pd.Timedelta(days=10)
    )

    add_defect(
        manifest,
        country_code,
        "booking",
        "travel_before_booking",
        defect_counts["bad_travel_date"],
        "Travel date deliberately occurs before booking date.",
    )

    df.loc[
        selected["invalid_status"],
        "booking_status",
    ] = "UNKNOWN"

    add_defect(
        manifest,
        country_code,
        "booking",
        "invalid_booking_status",
        defect_counts["invalid_status"],
        "Invalid booking status inserted.",
    )

    alias_values = {
        "MY": ["Flight", "HOTEL", "Car", "Misc"],
        "SG": ["AIR", "Lodging", "Car", "Misc"],
        "ID": ["Flight", "Accommodation", "Transport", "Misc"],
    }

    product_alias_indices = selected["product_alias"]

    df.loc[
        product_alias_indices,
        "product_type",
    ] = rng.choice(
        alias_values[country_code],
        size=len(product_alias_indices),
    )

    add_defect(
        manifest,
        country_code,
        "booking",
        "inconsistent_product_category",
        defect_counts["product_alias"],
        "Alternative product descriptions deliberately inserted.",
    )

    duplicate_count = max(
        10,
        int(n * 0.0005),
    )

    duplicate_indices = rng.choice(
        df.index,
        size=duplicate_count,
        replace=False,
    )

    duplicates = df.loc[
        duplicate_indices
    ].copy()

    df = pd.concat(
        [df, duplicates],
        ignore_index=True,
    )

    add_defect(
        manifest,
        country_code,
        "booking",
        "duplicate_transaction",
        duplicate_count,
        "Exact duplicate transaction rows appended.",
    )

    return df


def convert_malaysia_schema(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    return bookings.copy()


def convert_singapore_schema(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    df = bookings.rename(
        columns={
            "booking_id": "transaction_ref",
            "booking_date": "txn_date",
            "travel_date": "departure_date",
            "customer_id": "client_code",
            "supplier_id": "vendor_code",
            "product_type": "service_category",
            "booking_channel": "booking_method",
            "destination_country": "destination",
            "currency": "txn_currency",
            "booking_value": "gross_sales",
            "revenue": "net_revenue",
            "cost": "direct_cost",
            "booking_status": "status",
        }
    ).copy()

    df["booking_method"] = df[
        "booking_method"
    ].replace(
        {
            "Online": "OBT",
            "Offline": "Agent",
        }
    )

    return df.drop(
        columns=["agent_id"]
    )


def convert_indonesia_schema(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    df = bookings.rename(
        columns={
            "booking_id": "booking_no",
            "booking_date": "created_at",
            "travel_date": "journey_date",
            "customer_id": "account_no",
            "supplier_id": "provider_code",
            "product_type": "travel_product",
            "booking_channel": "channel",
            "destination_country": "destination",
            "currency": "currency_code",
            "booking_value": "total_booking_amount",
            "revenue": "service_revenue",
            "cost": "supplier_cost",
            "booking_status": "booking_state",
        }
    ).copy()

    df["channel"] = df[
        "channel"
    ].replace(
        {
            "Online": "ONLINE",
            "Offline": "MANUAL",
        }
    )

    return df.drop(
        columns=["agent_id"]
    )


def convert_singapore_customer_schema(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    return customers.rename(
        columns={
            "customer_id": "client_code",
            "customer_name": "client_name",
            "segment": "customer_tier",
            "industry": "sector",
            "account_manager": "relationship_manager",
            "contract_start_date": "effective_from",
            "contract_end_date": "effective_to",
            "status": "active_flag",
        }
    )


def convert_indonesia_customer_schema(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    return customers.rename(
        columns={
            "customer_id": "account_no",
            "customer_name": "account_name",
            "segment": "account_segment",
            "industry": "business_sector",
            "account_manager": "account_owner",
            "contract_start_date": "start_date",
            "contract_end_date": "end_date",
            "status": "account_status",
        }
    )


def convert_singapore_supplier_schema(
    suppliers: pd.DataFrame,
) -> pd.DataFrame:
    return suppliers.rename(
        columns={
            "supplier_id": "vendor_code",
            "supplier_name": "vendor_name",
            "supplier_type": "vendor_category",
            "preferred_supplier_flag": "preferred_flag",
            "country": "vendor_country",
            "status": "active_flag",
        }
    )


def convert_indonesia_supplier_schema(
    suppliers: pd.DataFrame,
) -> pd.DataFrame:
    return suppliers.rename(
        columns={
            "supplier_id": "provider_code",
            "supplier_name": "provider_name",
            "supplier_type": "provider_type",
            "preferred_supplier_flag": "preferred",
            "country": "provider_country",
            "status": "provider_status",
        }
    )


def convert_singapore_finance_schema(
    finance: pd.DataFrame,
) -> pd.DataFrame:
    return finance.rename(
        columns={
            "finance_month": "period",
            "country": "market",
            "revenue": "sales_revenue",
            "cost": "operating_cost",
            "gross_margin": "margin",
            "transaction_count": "transactions",
        }
    )


def convert_indonesia_finance_schema(
    finance: pd.DataFrame,
) -> pd.DataFrame:
    return finance.rename(
        columns={
            "finance_month": "accounting_period",
            "country": "country_code",
            "revenue": "reported_revenue",
            "cost": "reported_cost",
            "gross_margin": "reported_margin",
            "transaction_count": "reported_transactions",
        }
    )


def make_malaysia_payments(
    bookings: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    confirmed = bookings.loc[
        bookings["booking_status"] == "Confirmed"
    ].copy()

    sample_size = min(
        len(confirmed),
        50000,
    )

    selected = confirmed.sample(
        n=sample_size,
        random_state=42,
    )

    payment_delay = rng.integers(
        0,
        15,
        size=sample_size,
    )

    payment_date = (
        pd.to_datetime(selected["booking_date"])
        + pd.to_timedelta(
            payment_delay,
            unit="D",
        )
    )

    payments = pd.DataFrame(
        {
            "payment_id": [
                f"MY-P{i:08d}"
                for i in range(1, sample_size + 1)
            ],
            "booking_id": selected[
                "booking_id"
            ].to_numpy(),
            "payment_date": payment_date.to_numpy(),
            "payment_method": rng.choice(
                [
                    "Corporate Card",
                    "Bank Transfer",
                    "Invoice",
                ],
                size=sample_size,
                p=[0.45, 0.20, 0.35],
            ),
            "payment_amount": selected[
                "booking_value"
            ].to_numpy(),
            "payment_status": rng.choice(
                ["Settled", "Pending", "Failed"],
                size=sample_size,
                p=[0.96, 0.03, 0.01],
            ),
        }
    )

    payments["settlement_date"] = (
        payments["payment_date"]
        + pd.to_timedelta(
            rng.integers(
                1,
                6,
                size=sample_size,
            ),
            unit="D",
        )
    )

    return payments


def save_country_data(
    country_code: str,
    bookings: pd.DataFrame,
    customers: pd.DataFrame,
    suppliers: pd.DataFrame,
    finance: pd.DataFrame,
    rng: np.random.Generator,
) -> None:
    country_folder = {
        "MY": "malaysia",
        "SG": "singapore",
        "ID": "indonesia",
    }[country_code]

    output_dir = RAW_DIR / country_folder
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if country_code == "MY":
        convert_malaysia_schema(
            bookings
        ).to_csv(
            output_dir / "bookings.csv",
            index=False,
        )

        customers.to_excel(
            output_dir / "customers.xlsx",
            index=False,
        )

        suppliers.to_csv(
            output_dir / "suppliers.csv",
            index=False,
        )

        finance.to_csv(
            output_dir / "finance.csv",
            index=False,
        )

        payments = make_malaysia_payments(
            bookings,
            rng,
        )

        payments.to_csv(
            output_dir / "payments.csv",
            index=False,
        )

    elif country_code == "SG":
        convert_singapore_schema(
            bookings
        ).to_excel(
            output_dir / "transactions.xlsx",
            index=False,
        )

        convert_singapore_customer_schema(
            customers
        ).to_csv(
            output_dir / "client_master.csv",
            index=False,
        )

        convert_singapore_supplier_schema(
            suppliers
        ).to_excel(
            output_dir / "vendor_master.xlsx",
            index=False,
        )

        convert_singapore_finance_schema(
            finance
        ).to_csv(
            output_dir / "finance_extract.csv",
            index=False,
        )

    elif country_code == "ID":
        convert_indonesia_schema(
            bookings
        ).to_csv(
            output_dir / "booking_export.csv",
            index=False,
        )

        convert_indonesia_customer_schema(
            customers
        ).to_excel(
            output_dir / "accounts.xlsx",
            index=False,
        )

        convert_indonesia_supplier_schema(
            suppliers
        ).to_csv(
            output_dir / "supplier_export.csv",
            index=False,
        )

        convert_indonesia_finance_schema(
            finance
        ).to_csv(
            output_dir / "finance_id.csv",
            index=False,
        )


def main() -> None:
    config = load_config()

    rng = np.random.default_rng(
        config["random_seed"]
    )

    manifest = []

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:
        print(
            f"\nGenerating {country_code}..."
        )

        customers = make_customer_master(
            country_code,
            CUSTOMER_COUNTS[country_code],
            rng,
        )

        suppliers = make_supplier_master(
            country_code,
            SUPPLIER_COUNTS[country_code],
            rng,
        )

        target_rows = config[
            "countries"
        ][country_code][
            "target_booking_rows"
        ]

        clean_bookings = make_booking_data(
            country_code,
            target_rows,
            customers,
            suppliers,
            config,
            rng,
        )

        finance = make_finance_data(
            clean_bookings,
            country_code,
            rng,
        )

        raw_bookings = inject_booking_defects(
            clean_bookings,
            country_code,
            rng,
            manifest,
        )

        save_country_data(
            country_code,
            raw_bookings,
            customers,
            suppliers,
            finance,
            rng,
        )

        print(
            f"{country_code}: "
            f"{len(raw_bookings):,} raw booking rows"
        )

        print(
            f"{country_code}: "
            f"{len(customers):,} customers"
        )

        print(
            f"{country_code}: "
            f"{len(suppliers):,} suppliers"
        )

    manifest_df = pd.DataFrame(
        manifest
    )

    manifest_df.to_csv(
        REFERENCE_DIR / "defect_manifest.csv",
        index=False,
    )

    print(
        "\nSynthetic raw-data generation completed."
    )

    print(
        f"Defect manifest: "
        f"{len(manifest_df):,} defect definitions"
    )


if __name__ == "__main__":
    main()