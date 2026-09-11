from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
MY_DIR = RAW_DIR / "malaysia"
SG_DIR = RAW_DIR / "singapore"
ID_DIR = RAW_DIR / "indonesia"

DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.json"

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)

fake = Faker()
Faker.seed(RANDOM_SEED)

DEFAULT_START_DATE = "2024-09-01"
DEFAULT_END_DATE = "2026-08-31"

COUNTRY_CONFIG = {
    "MY": {
        "country_name": "Malaysia",
        "currency": "MYR",
        "booking_rows": 80_000,
        "customers": 320,
        "suppliers": 80,
    },
    "SG": {
        "country_name": "Singapore",
        "currency": "SGD",
        "booking_rows": 50_000,
        "customers": 220,
        "suppliers": 60,
    },
    "ID": {
        "country_name": "Indonesia",
        "currency": "IDR",
        "booking_rows": 50_000,
        "customers": 260,
        "suppliers": 70,
    },
}

PRODUCTS = [
    "Air",
    "Hotel",
    "Ground",
    "Other",
]

PRODUCT_PROBABILITIES = [
    0.54,
    0.29,
    0.11,
    0.06,
]

CHANNELS = [
    "Online",
    "Offline",
]

CHANNEL_PROBABILITIES = [
    0.58,
    0.42,
]

BOOKING_STATUSES = [
    "Confirmed",
    "Cancelled",
    "Refunded",
]

STATUS_PROBABILITIES = [
    0.94,
    0.04,
    0.02,
]

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

CUSTOMER_SEGMENTS = [
    "Strategic",
    "Enterprise",
    "Mid-Market",
    "SME",
]

INDUSTRIES = [
    "Technology",
    "Manufacturing",
    "Financial Services",
    "Professional Services",
    "Healthcare",
    "Energy",
    "Retail",
    "Education",
    "Government",
    "Logistics",
]

SUPPLIER_TYPES = [
    "Airline",
    "Hotel",
    "Ground Transport",
    "Travel Service",
]


# ============================================================
# DIRECTORY SETUP
# ============================================================


def ensure_directories() -> None:
    for directory in [
        MY_DIR,
        SG_DIR,
        ID_DIR,
        DOCS_DIR,
    ]:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


# ============================================================
# PROJECT DATE CONFIGURATION
# ============================================================


def load_project_dates() -> tuple[pd.Timestamp, pd.Timestamp]:
    start_date = pd.Timestamp(DEFAULT_START_DATE)
    end_date = pd.Timestamp(DEFAULT_END_DATE)

    if CONFIG_PATH.exists():
        try:
            config = json.loads(
                CONFIG_PATH.read_text(
                    encoding="utf-8"
                )
            )

            start_date = pd.Timestamp(
                config.get(
                    "start_date",
                    DEFAULT_START_DATE,
                )
            )

            end_date = pd.Timestamp(
                config.get(
                    "end_date",
                    DEFAULT_END_DATE,
                )
            )

        except Exception:
            pass

    return start_date, end_date


# ============================================================
# RANDOM HELPERS
# ============================================================


def random_dates(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    n: int,
) -> pd.Series:
    start_ns = start_date.value
    end_ns = end_date.value

    values = np.random.randint(
        start_ns,
        end_ns + 1,
        size=n,
        dtype=np.int64,
    )

    return pd.Series(
        pd.to_datetime(values)
    ).dt.normalize()


def sample_indices(
    df: pd.DataFrame,
    fraction: float,
    minimum: int = 1,
) -> np.ndarray:
    count = max(
        minimum,
        int(
            round(
                len(df) * fraction
            )
        ),
    )

    count = min(
        count,
        len(df),
    )

    return np.random.choice(
        df.index.to_numpy(),
        size=count,
        replace=False,
    )


# ============================================================
# CUSTOMER MASTER GENERATION
# ============================================================


def create_customer_master(
    country_code: str,
    customer_count: int,
) -> pd.DataFrame:
    rows = []

    for number in range(
        1,
        customer_count + 1,
    ):
        rows.append(
            {
                "customer_id": (
                    f"{country_code}-CUST-{number:04d}"
                ),
                "customer_name": (
                    f"{fake.company()} {country_code}"
                ),
                "segment": np.random.choice(
                    CUSTOMER_SEGMENTS
                ),
                "industry": np.random.choice(
                    INDUSTRIES
                ),
                "customer_status": np.random.choice(
                    [
                        "Active",
                        "Inactive",
                    ],
                    p=[
                        0.96,
                        0.04,
                    ],
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# SUPPLIER MASTER GENERATION
# ============================================================


def create_supplier_master(
    country_code: str,
    supplier_count: int,
) -> pd.DataFrame:
    rows = []

    for number in range(
        1,
        supplier_count + 1,
    ):
        rows.append(
            {
                "supplier_id": (
                    f"{country_code}-SUP-{number:03d}"
                ),
                "supplier_name": (
                    f"Synthetic Supplier "
                    f"{country_code} "
                    f"{number:03d}"
                ),
                "supplier_type": np.random.choice(
                    SUPPLIER_TYPES
                ),
                "preferred_flag": np.random.choice(
                    [
                        "Y",
                        "N",
                    ],
                    p=[
                        0.70,
                        0.30,
                    ],
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# CLEAN SYNTHETIC BOOKING GENERATION
# ============================================================


def generate_clean_bookings(
    country_code: str,
    row_count: int,
    customers: pd.DataFrame,
    suppliers: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    booking_dates = random_dates(
        start_date=start_date,
        end_date=end_date,
        n=row_count,
    )

    advance_purchase_days = np.random.gamma(
        shape=2.4,
        scale=8.0,
        size=row_count,
    )

    advance_purchase_days = np.clip(
        np.round(
            advance_purchase_days
        ),
        0,
        180,
    ).astype(int)

    travel_dates = (
        booking_dates
        + pd.to_timedelta(
            advance_purchase_days,
            unit="D",
        )
    )

    products = np.random.choice(
        PRODUCTS,
        size=row_count,
        p=PRODUCT_PROBABILITIES,
    )

    channels = np.random.choice(
        CHANNELS,
        size=row_count,
        p=CHANNEL_PROBABILITIES,
    )

    statuses = np.random.choice(
        BOOKING_STATUSES,
        size=row_count,
        p=STATUS_PROBABILITIES,
    )

    booking_value = np.random.lognormal(
        mean=7.7,
        sigma=0.80,
        size=row_count,
    )

    if country_code == "SG":
        booking_value *= 0.72

    elif country_code == "ID":
        booking_value *= 5_500.0

    revenue_rate = np.random.uniform(
        0.06,
        0.16,
        size=row_count,
    )

    revenue = (
        booking_value
        * revenue_rate
    )

    cost_ratio = np.random.uniform(
        0.55,
        0.88,
        size=row_count,
    )

    cost = (
        revenue
        * cost_ratio
    )

    cancelled_mask = (
        statuses == "Cancelled"
    )

    revenue[
        cancelled_mask
    ] = 0.0

    cost[
        cancelled_mask
    ] = 0.0

    refunded_mask = (
        statuses == "Refunded"
    )

    revenue[
        refunded_mask
    ] = -np.abs(
        revenue[
            refunded_mask
        ]
    )

    cost[
        refunded_mask
    ] = -np.abs(
        cost[
            refunded_mask
        ]
    )

    bookings = pd.DataFrame(
        {
            "booking_id": [
                (
                    f"{country_code}-"
                    f"BK-{number:07d}"
                )
                for number in range(
                    1,
                    row_count + 1,
                )
            ],
            "booking_date": booking_dates,
            "travel_date": travel_dates,
            "customer_id": np.random.choice(
                customers[
                    "customer_id"
                ],
                size=row_count,
            ),
            "supplier_id": np.random.choice(
                suppliers[
                    "supplier_id"
                ],
                size=row_count,
            ),
            "product_type": products,
            "booking_channel": channels,
            "destination_country": np.random.choice(
                DESTINATIONS,
                size=row_count,
            ),
            "currency": COUNTRY_CONFIG[
                country_code
            ][
                "currency"
            ],
            "booking_value": np.round(
                booking_value,
                2,
            ),
            "revenue": np.round(
                revenue,
                2,
            ),
            "cost": np.round(
                cost,
                2,
            ),
            "booking_status": statuses,
        }
    )

    return bookings


# ============================================================
# FINANCE SOURCE GENERATION
# ============================================================


def create_finance_truth(
    bookings: pd.DataFrame,
    country_code: str,
) -> pd.DataFrame:
    working = bookings.copy()

    working[
        "finance_month"
    ] = (
        pd.to_datetime(
            working[
                "booking_date"
            ]
        )
        .dt.to_period(
            "M"
        )
        .dt.to_timestamp()
    )

    finance = (
        working.groupby(
            "finance_month",
            as_index=False,
        )
        .agg(
            revenue=(
                "revenue",
                "sum",
            ),
            cost=(
                "cost",
                "sum",
            ),
            transaction_count=(
                "booking_id",
                "count",
            ),
        )
    )

    finance[
        "gross_margin"
    ] = (
        finance[
            "revenue"
        ]
        - finance[
            "cost"
        ]
    )

    revenue_adjustment = np.random.normal(
        loc=1.0,
        scale=0.004,
        size=len(finance),
    )

    cost_adjustment = np.random.normal(
        loc=1.0,
        scale=0.004,
        size=len(finance),
    )

    transaction_adjustment = np.random.choice(
        [
            -2,
            -1,
            0,
            0,
            0,
            1,
            2,
        ],
        size=len(finance),
    )

    finance[
        "revenue"
    ] = np.round(
        finance[
            "revenue"
        ]
        * revenue_adjustment,
        2,
    )

    finance[
        "cost"
    ] = np.round(
        finance[
            "cost"
        ]
        * cost_adjustment,
        2,
    )

    finance[
        "gross_margin"
    ] = np.round(
        finance[
            "revenue"
        ]
        - finance[
            "cost"
        ],
        2,
    )

    finance[
        "transaction_count"
    ] = (
        finance[
            "transaction_count"
        ]
        + transaction_adjustment
    ).astype(int)

    finance[
        "country"
    ] = country_code

    return finance[
        [
            "finance_month",
            "country",
            "revenue",
            "cost",
            "gross_margin",
            "transaction_count",
        ]
    ]


# ============================================================
# DELIBERATE DATA QUALITY DEFECTS
# ============================================================


def inject_booking_defects(
    bookings: pd.DataFrame,
    country_code: str,
    valid_customers: set[str],
    valid_suppliers: set[str],
) -> tuple[pd.DataFrame, list[dict]]:
    df = bookings.copy()
    manifest: list[dict] = []

    indices = sample_indices(
        df,
        fraction=0.00030,
    )

    df.loc[
        indices,
        "customer_id",
    ] = pd.NA

    manifest.append(
        {
            "country": country_code,
            "defect": "MISSING_CUSTOMER_ID",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00030,
    )

    df.loc[
        indices,
        "supplier_id",
    ] = pd.NA

    manifest.append(
        {
            "country": country_code,
            "defect": "MISSING_SUPPLIER_ID",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00020,
    )

    for sequence, index in enumerate(
        indices,
        start=1,
    ):
        orphan_value = (
            f"{country_code}-"
            f"ORPHAN-CUST-"
            f"{sequence:03d}"
        )

        if orphan_value not in valid_customers:
            df.at[
                index,
                "customer_id",
            ] = orphan_value

    manifest.append(
        {
            "country": country_code,
            "defect": "ORPHAN_CUSTOMER",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00020,
    )

    for sequence, index in enumerate(
        indices,
        start=1,
    ):
        orphan_value = (
            f"{country_code}-"
            f"ORPHAN-SUP-"
            f"{sequence:03d}"
        )

        if orphan_value not in valid_suppliers:
            df.at[
                index,
                "supplier_id",
            ] = orphan_value

    manifest.append(
        {
            "country": country_code,
            "defect": "ORPHAN_SUPPLIER",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00020,
    )

    df.loc[
        indices,
        "currency",
    ] = "XXX"

    manifest.append(
        {
            "country": country_code,
            "defect": "INVALID_CURRENCY",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00020,
    )

    df.loc[
        indices,
        "booking_value",
    ] = -np.abs(
        df.loc[
            indices,
            "booking_value",
        ]
    )

    manifest.append(
        {
            "country": country_code,
            "defect": "NEGATIVE_BOOKING_VALUE",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00020,
    )

    df.loc[
        indices,
        "booking_status",
    ] = "UNKNOWN"

    manifest.append(
        {
            "country": country_code,
            "defect": "INVALID_BOOKING_STATUS",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00030,
    )

    df.loc[
        indices,
        "travel_date",
    ] = (
        pd.to_datetime(
            df.loc[
                indices,
                "booking_date",
            ]
        )
        - pd.to_timedelta(
            5,
            unit="D",
        )
    )

    manifest.append(
        {
            "country": country_code,
            "defect": "INVALID_TRAVEL_DATE",
            "records_injected": len(indices),
        }
    )

    indices = sample_indices(
        df,
        fraction=0.00050,
    )

    if country_code == "MY":
        invalid_products = [
            "AIR",
            "Lodging",
            "Misc",
            "Car",
        ]

    elif country_code == "SG":
        invalid_products = [
            "Air Ticket",
            "AIR",
            "Misc",
            "Lodging",
            "Car",
        ]

    else:
        invalid_products = [
            "Flight",
            "Accommodation",
            "Transport",
            "Misc",
        ]

    df.loc[
        indices,
        "product_type",
    ] = np.random.choice(
        invalid_products,
        size=len(indices),
    )

    manifest.append(
        {
            "country": country_code,
            "defect": "UNMAPPED_PRODUCT",
            "records_injected": len(indices),
        }
    )

    duplicate_count = max(
        1,
        int(
            round(
                len(df)
                * 0.00050
            )
        ),
    )

    country_seed = {
        "MY": 1,
        "SG": 2,
        "ID": 3,
    }

    duplicate_rows = (
        df.sample(
            n=duplicate_count,
            random_state=(
                RANDOM_SEED
                + country_seed[
                    country_code
                ]
            ),
        )
        .copy()
    )

    df = pd.concat(
        [
            df,
            duplicate_rows,
        ],
        ignore_index=True,
    )

    manifest.append(
        {
            "country": country_code,
            "defect": "DUPLICATE_ROWS_APPENDED",
            "records_injected": duplicate_count,
        }
    )

    return df, manifest


# ============================================================
# COUNTRY-SPECIFIC TERMINOLOGY
# ============================================================


def apply_country_terminology(
    df: pd.DataFrame,
    country_code: str,
) -> pd.DataFrame:
    result = df.copy()

    if country_code == "MY":
        product_mapping = {
            "Air": "Air",
            "Hotel": "Hotel",
            "Ground": "Ground",
            "Other": "Other",
        }

        channel_mapping = {
            "Online": "Online",
            "Offline": "Offline",
        }

    elif country_code == "SG":
        product_mapping = {
            "Air": "Flight",
            "Hotel": "Accommodation",
            "Ground": "Transport",
            "Other": "Other Service",
        }

        channel_mapping = {
            "Online": "OBT",
            "Offline": "Agent",
        }

    elif country_code == "ID":
        product_mapping = {
            "Air": "AIR",
            "Hotel": "HOTEL",
            "Ground": "GROUND",
            "Other": "OTHER",
        }

        channel_mapping = {
            "Online": "ONLINE",
            "Offline": "MANUAL",
        }

    else:
        raise ValueError(
            f"Unsupported country: {country_code}"
        )

    result[
        "product_type"
    ] = (
        result[
            "product_type"
        ]
        .replace(
            product_mapping
        )
    )

    result[
        "booking_channel"
    ] = (
        result[
            "booking_channel"
        ]
        .replace(
            channel_mapping
        )
    )

    return result


# ============================================================
# MALAYSIA RAW BOOKING SCHEMA
# ============================================================


def convert_my_booking_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    return df[
        [
            "booking_id",
            "booking_date",
            "travel_date",
            "customer_id",
            "supplier_id",
            "product_type",
            "booking_channel",
            "destination_country",
            "currency",
            "booking_value",
            "revenue",
            "cost",
            "booking_status",
        ]
    ].copy()


# ============================================================
# SINGAPORE RAW BOOKING SCHEMA
# ============================================================


def convert_sg_booking_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.rename(
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

    return result[
        [
            "transaction_ref",
            "txn_date",
            "departure_date",
            "client_code",
            "vendor_code",
            "service_category",
            "booking_method",
            "destination",
            "txn_currency",
            "gross_sales",
            "net_revenue",
            "direct_cost",
            "status",
        ]
    ]


# ============================================================
# INDONESIA RAW BOOKING SCHEMA
# ============================================================


def convert_id_booking_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.rename(
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

    return result[
        [
            "booking_no",
            "created_at",
            "journey_date",
            "account_no",
            "provider_code",
            "travel_product",
            "channel",
            "destination",
            "currency_code",
            "total_booking_amount",
            "service_revenue",
            "supplier_cost",
            "booking_state",
        ]
    ]


# ============================================================
# CUSTOMER MASTER FILES
# ============================================================


def write_customer_files(
    customer_data: dict[str, pd.DataFrame],
) -> None:

    # Malaysia
    my = customer_data[
        "MY"
    ].copy()

    my[
        "account_manager"
    ] = [
        f"MY Account Manager {(i % 12) + 1:02d}"
        for i in range(len(my))
    ]

    my = my.rename(
        columns={
            "customer_status": "status",
        }
    )

    my = my[
        [
            "customer_id",
            "customer_name",
            "segment",
            "industry",
            "account_manager",
            "status",
        ]
    ]

    my.to_excel(
        MY_DIR / "customers.xlsx",
        index=False,
    )

    # Singapore
    sg = customer_data[
        "SG"
    ].copy()

    sg[
        "relationship_manager"
    ] = [
        f"SG Relationship Manager {(i % 10) + 1:02d}"
        for i in range(len(sg))
    ]

    sg = sg.rename(
        columns={
            "customer_id": "client_code",
            "customer_name": "client_name",
            "segment": "customer_tier",
            "industry": "sector",
            "customer_status": "active_flag",
        }
    )

    sg = sg[
        [
            "client_code",
            "client_name",
            "customer_tier",
            "sector",
            "relationship_manager",
            "active_flag",
        ]
    ]

    sg.to_csv(
        SG_DIR / "client_master.csv",
        index=False,
    )

    # Indonesia
    idn = customer_data[
        "ID"
    ].copy()

    idn[
        "account_owner"
    ] = [
        f"ID Account Owner {(i % 11) + 1:02d}"
        for i in range(len(idn))
    ]

    idn = idn.rename(
        columns={
            "customer_id": "account_no",
            "customer_name": "account_name",
            "segment": "account_segment",
            "industry": "business_sector",
            "customer_status": "account_status",
        }
    )

    idn = idn[
        [
            "account_no",
            "account_name",
            "account_segment",
            "business_sector",
            "account_owner",
            "account_status",
        ]
    ]

    idn.to_excel(
        ID_DIR / "accounts.xlsx",
        index=False,
    )


# ============================================================
# SUPPLIER MASTER FILES
# ============================================================


def write_supplier_files(
    supplier_data: dict[str, pd.DataFrame],
) -> None:

    # Malaysia
    my = supplier_data[
        "MY"
    ].copy()

    my[
        "status"
    ] = np.random.choice(
        [
            "Active",
            "Inactive",
        ],
        size=len(my),
        p=[
            0.96,
            0.04,
        ],
    )

    my = my.rename(
        columns={
            "preferred_flag":
                "preferred_supplier_flag",
        }
    )

    my = my[
        [
            "supplier_id",
            "supplier_name",
            "supplier_type",
            "preferred_supplier_flag",
            "status",
        ]
    ]

    my.to_csv(
        MY_DIR / "suppliers.csv",
        index=False,
    )

    # Singapore
    sg = supplier_data[
        "SG"
    ].copy()

    sg[
        "active_flag"
    ] = np.random.choice(
        [
            "Active",
            "Inactive",
        ],
        size=len(sg),
        p=[
            0.96,
            0.04,
        ],
    )

    sg = sg.rename(
        columns={
            "supplier_id": "vendor_code",
            "supplier_name": "vendor_name",
            "supplier_type": "vendor_category",
        }
    )

    sg = sg[
        [
            "vendor_code",
            "vendor_name",
            "vendor_category",
            "preferred_flag",
            "active_flag",
        ]
    ]

    sg.to_excel(
        SG_DIR / "vendor_master.xlsx",
        index=False,
    )

    # Indonesia
    idn = supplier_data[
        "ID"
    ].copy()

    idn[
        "provider_status"
    ] = np.random.choice(
        [
            "Active",
            "Inactive",
        ],
        size=len(idn),
        p=[
            0.96,
            0.04,
        ],
    )

    idn = idn.rename(
        columns={
            "supplier_id": "provider_code",
            "supplier_name": "provider_name",
            "supplier_type": "provider_type",
            "preferred_flag": "preferred",
        }
    )

    idn = idn[
        [
            "provider_code",
            "provider_name",
            "provider_type",
            "preferred",
            "provider_status",
        ]
    ]

    idn.to_csv(
        ID_DIR / "supplier_export.csv",
        index=False,
    )


# ============================================================
# FINANCE FILES
# ============================================================


def write_finance_files(
    finance_data: dict[str, pd.DataFrame],
) -> None:

    finance_data[
        "MY"
    ].to_csv(
        MY_DIR / "finance.csv",
        index=False,
    )

    sg = finance_data[
        "SG"
    ].rename(
        columns={
            "finance_month": "period",
            "country": "market",
            "revenue": "sales_revenue",
            "cost": "operating_cost",
            "gross_margin": "margin",
            "transaction_count": "transactions",
        }
    )

    sg.to_csv(
        SG_DIR / "finance_extract.csv",
        index=False,
    )

    idn = finance_data[
        "ID"
    ].rename(
        columns={
            "finance_month": "accounting_period",
            "country": "country_code",
            "revenue": "reported_revenue",
            "cost": "reported_cost",
            "gross_margin": "reported_margin",
            "transaction_count": "reported_transactions",
        }
    )

    idn.to_csv(
        ID_DIR / "finance_id.csv",
        index=False,
    )


# ============================================================
# MALAYSIA PAYMENT DATA
# ============================================================


def create_my_payments(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    working = bookings[
        [
            "booking_id",
            "booking_date",
            "booking_value",
            "booking_status",
        ]
    ].copy()

    working[
        "payment_id"
    ] = [
        f"MY-PAY-{number:07d}"
        for number in range(
            1,
            len(working) + 1,
        )
    ]

    working[
        "payment_method"
    ] = np.random.choice(
        [
            "Corporate Card",
            "Bank Transfer",
            "Virtual Card",
            "Invoice",
        ],
        size=len(working),
        p=[
            0.30,
            0.20,
            0.25,
            0.25,
        ],
    )

    working[
        "payment_date"
    ] = (
        pd.to_datetime(
            working[
                "booking_date"
            ]
        )
        + pd.to_timedelta(
            np.random.randint(
                0,
                10,
                size=len(working),
            ),
            unit="D",
        )
    )

    working[
        "paid_amount"
    ] = np.where(
        working[
            "booking_status"
        ].eq(
            "Cancelled"
        ),
        0.0,
        working[
            "booking_value"
        ],
    )

    working[
        "refund_amount"
    ] = np.where(
        working[
            "booking_status"
        ].eq(
            "Refunded"
        ),
        np.abs(
            working[
                "booking_value"
            ]
        ),
        0.0,
    )

    return working[
        [
            "payment_id",
            "booking_id",
            "payment_method",
            "payment_date",
            "paid_amount",
            "refund_amount",
        ]
    ]


# ============================================================
# DEFECT MANIFEST
# ============================================================


def write_defect_manifest(
    manifest_rows: list[dict],
) -> None:
    manifest = pd.DataFrame(
        manifest_rows
    )

    manifest.to_csv(
        DOCS_DIR
        / "synthetic_defect_manifest.csv",
        index=False,
    )

    markdown_path = (
        DOCS_DIR
        / "synthetic_defect_manifest.md"
    )

    lines = [
        "# Synthetic Defect Manifest",
        "",
        (
            "Independent synthetic case study. "
            "No Peter Stuyvesant Travel "
            "confidential data, customer "
            "information or internal systems "
            "are used."
        ),
        "",
        (
            "This document records intentional "
            "data-quality defects injected into "
            "the fictional source datasets."
        ),
        "",
        "| Country | Defect | Records Injected |",
        "|---|---|---:|",
    ]

    for row in manifest_rows:
        lines.append(
            (
                f"| {row['country']} "
                f"| {row['defect']} "
                f"| {row['records_injected']} |"
            )
        )

    markdown_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# ============================================================
# GENERATED DATA VALIDATION
# ============================================================


def validate_generated_files() -> None:
    my = pd.read_csv(
        MY_DIR / "bookings.csv"
    )

    sg = pd.read_excel(
        SG_DIR / "transactions.xlsx"
    )

    idn = pd.read_csv(
        ID_DIR / "booking_export.csv"
    )

    expected_my_columns = [
        "booking_id",
        "booking_date",
        "travel_date",
        "customer_id",
        "supplier_id",
        "product_type",
        "booking_channel",
        "destination_country",
        "currency",
        "booking_value",
        "revenue",
        "cost",
        "booking_status",
    ]

    expected_sg_columns = [
        "transaction_ref",
        "txn_date",
        "departure_date",
        "client_code",
        "vendor_code",
        "service_category",
        "booking_method",
        "destination",
        "txn_currency",
        "gross_sales",
        "net_revenue",
        "direct_cost",
        "status",
    ]

    expected_id_columns = [
        "booking_no",
        "created_at",
        "journey_date",
        "account_no",
        "provider_code",
        "travel_product",
        "channel",
        "destination",
        "currency_code",
        "total_booking_amount",
        "service_revenue",
        "supplier_cost",
        "booking_state",
    ]

    if my.columns.tolist() != expected_my_columns:
        raise RuntimeError(
            "Malaysia booking schema mismatch."
        )

    if sg.columns.tolist() != expected_sg_columns:
        raise RuntimeError(
            "Singapore booking schema mismatch."
        )

    if idn.columns.tolist() != expected_id_columns:
        raise RuntimeError(
            "Indonesia booking schema mismatch."
        )

    expected_sg_products = {
        "Flight",
        "Accommodation",
        "Transport",
        "Other Service",
    }

    expected_id_products = {
        "AIR",
        "HOTEL",
        "GROUND",
        "OTHER",
    }

    actual_sg_products = set(
        sg[
            "service_category"
        ]
        .dropna()
        .unique()
    )

    actual_id_products = set(
        idn[
            "travel_product"
        ]
        .dropna()
        .unique()
    )

    if not expected_sg_products.issubset(
        actual_sg_products
    ):
        raise RuntimeError(
            "Singapore normal product labels missing."
        )

    if not expected_id_products.issubset(
        actual_id_products
    ):
        raise RuntimeError(
            "Indonesia normal product labels missing."
        )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    ensure_directories()

    start_date, end_date = (
        load_project_dates()
    )

    print(
        "Generating independent synthetic regional travel data..."
    )

    print(
        (
            f"Period: "
            f"{start_date.date()} "
            f"to "
            f"{end_date.date()}"
        )
    )

    customer_data = {}
    supplier_data = {}
    clean_booking_data = {}
    finance_data = {}
    raw_booking_data = {}
    manifest_rows = []

    for (
        country_code,
        config,
    ) in COUNTRY_CONFIG.items():

        customers = create_customer_master(
            country_code=country_code,
            customer_count=config[
                "customers"
            ],
        )

        suppliers = create_supplier_master(
            country_code=country_code,
            supplier_count=config[
                "suppliers"
            ],
        )

        bookings = generate_clean_bookings(
            country_code=country_code,
            row_count=config[
                "booking_rows"
            ],
            customers=customers,
            suppliers=suppliers,
            start_date=start_date,
            end_date=end_date,
        )

        finance = create_finance_truth(
            bookings=bookings,
            country_code=country_code,
        )

        customer_data[
            country_code
        ] = customers

        supplier_data[
            country_code
        ] = suppliers

        clean_booking_data[
            country_code
        ] = bookings

        finance_data[
            country_code
        ] = finance

        defective, defects = (
            inject_booking_defects(
                bookings=bookings,
                country_code=country_code,
                valid_customers=set(
                    customers[
                        "customer_id"
                    ]
                ),
                valid_suppliers=set(
                    suppliers[
                        "supplier_id"
                    ]
                ),
            )
        )

        defective = (
            apply_country_terminology(
                defective,
                country_code,
            )
        )

        raw_booking_data[
            country_code
        ] = defective

        manifest_rows.extend(
            defects
        )

    write_customer_files(
        customer_data
    )

    write_supplier_files(
        supplier_data
    )

    my_raw = convert_my_booking_schema(
        raw_booking_data[
            "MY"
        ]
    )

    my_raw.to_csv(
        MY_DIR / "bookings.csv",
        index=False,
    )

    sg_raw = convert_sg_booking_schema(
        raw_booking_data[
            "SG"
        ]
    )

    sg_raw.to_excel(
        SG_DIR / "transactions.xlsx",
        index=False,
    )

    id_raw = convert_id_booking_schema(
        raw_booking_data[
            "ID"
        ]
    )

    id_raw.to_csv(
        ID_DIR / "booking_export.csv",
        index=False,
    )

    write_finance_files(
        finance_data
    )

    payments = create_my_payments(
        clean_booking_data[
            "MY"
        ]
    )

    payments.to_csv(
        MY_DIR / "payments.csv",
        index=False,
    )

    write_defect_manifest(
        manifest_rows
    )

    validate_generated_files()

    print()
    print(
        "Synthetic data generation completed."
    )

    print()
    print(
        "Booking source row counts"
    )

    print(
        "-------------------------"
    )

    print(
        f"MY: {len(my_raw):,}"
    )

    print(
        f"SG: {len(sg_raw):,}"
    )

    print(
        f"ID: {len(id_raw):,}"
    )

    print()
    print(
        "Customer entities"
    )

    print(
        "-----------------"
    )

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:
        print(
            (
                f"{country_code}: "
                f"{len(customer_data[country_code]):,}"
            )
        )

    print()
    print(
        "Supplier entities"
    )

    print(
        "-----------------"
    )

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:
        print(
            (
                f"{country_code}: "
                f"{len(supplier_data[country_code]):,}"
            )
        )

    print()
    print(
        "Normal product terminology"
    )

    print(
        "--------------------------"
    )

    print(
        "MY: Air / Hotel / Ground / Other"
    )

    print(
        (
            "SG: Flight / Accommodation / "
            "Transport / Other Service"
        )
    )

    print(
        "ID: AIR / HOTEL / GROUND / OTHER"
    )

    print()
    print(
        "Raw booking schemas"
    )

    print(
        "-------------------"
    )

    print(
        (
            "MY: booking_id / booking_date / "
            "travel_date / ..."
        )
    )

    print(
        (
            "SG: transaction_ref / txn_date / "
            "departure_date / ..."
        )
    )

    print(
        (
            "ID: booking_no / created_at / "
            "journey_date / ... / booking_state"
        )
    )

    print()
    print(
        "Raw data written under:"
    )

    print(
        RAW_DIR.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()