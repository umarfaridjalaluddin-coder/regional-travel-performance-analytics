from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"


# ---------------------------------------------------------------------
# SYNTHETIC PORTFOLIO ASSUMPTIONS
# ---------------------------------------------------------------------
#
# These numbers are NOT real-company characteristics.
#
# For demonstration purposes:
#
# - First 120 customers in each country are treated as entities belonging
#   to shared regional corporate groups.
#
# - First 25 suppliers in each country are treated as entities belonging
#   to shared regional supplier groups.
#
# Remaining entities are treated as locally unique.
#
# In a production environment these relationships would normally come
# from approved CRM, legal-entity, procurement or master-data mappings.
# ---------------------------------------------------------------------

SHARED_CUSTOMER_GROUPS = 120
SHARED_SUPPLIER_GROUPS = 25


def load_customer_masters() -> dict[str, pd.DataFrame]:

    my = pd.read_excel(
        RAW_DIR / "malaysia" / "customers.xlsx"
    )

    sg = pd.read_csv(
        RAW_DIR / "singapore" / "client_master.csv"
    )

    idn = pd.read_excel(
        RAW_DIR / "indonesia" / "accounts.xlsx"
    )

    my = my.rename(
        columns={
            "customer_id": "local_customer_id",
            "customer_name": "local_customer_name",
            "segment": "customer_segment",
            "industry": "industry",
            "account_manager": "account_owner",
            "status": "local_status",
        }
    )

    sg = sg.rename(
        columns={
            "client_code": "local_customer_id",
            "client_name": "local_customer_name",
            "customer_tier": "customer_segment",
            "sector": "industry",
            "relationship_manager": "account_owner",
            "active_flag": "local_status",
        }
    )

    idn = idn.rename(
        columns={
            "account_no": "local_customer_id",
            "account_name": "local_customer_name",
            "account_segment": "customer_segment",
            "business_sector": "industry",
            "account_owner": "account_owner",
            "account_status": "local_status",
        }
    )

    selected_columns = [
        "local_customer_id",
        "local_customer_name",
        "customer_segment",
        "industry",
        "account_owner",
        "local_status",
    ]

    return {
        "MY": my[selected_columns].copy(),
        "SG": sg[selected_columns].copy(),
        "ID": idn[selected_columns].copy(),
    }


def load_supplier_masters() -> dict[str, pd.DataFrame]:

    my = pd.read_csv(
        RAW_DIR / "malaysia" / "suppliers.csv"
    )

    sg = pd.read_excel(
        RAW_DIR / "singapore" / "vendor_master.xlsx"
    )

    idn = pd.read_csv(
        RAW_DIR / "indonesia" / "supplier_export.csv"
    )

    my = my.rename(
        columns={
            "supplier_id": "local_supplier_id",
            "supplier_name": "local_supplier_name",
            "supplier_type": "supplier_type",
            "preferred_supplier_flag": "preferred_flag",
            "status": "local_status",
        }
    )

    sg = sg.rename(
        columns={
            "vendor_code": "local_supplier_id",
            "vendor_name": "local_supplier_name",
            "vendor_category": "supplier_type",
            "preferred_flag": "preferred_flag",
            "active_flag": "local_status",
        }
    )

    idn = idn.rename(
        columns={
            "provider_code": "local_supplier_id",
            "provider_name": "local_supplier_name",
            "provider_type": "supplier_type",
            "preferred": "preferred_flag",
            "provider_status": "local_status",
        }
    )

    selected_columns = [
        "local_supplier_id",
        "local_supplier_name",
        "supplier_type",
        "preferred_flag",
        "local_status",
    ]

    return {
        "MY": my[selected_columns].copy(),
        "SG": sg[selected_columns].copy(),
        "ID": idn[selected_columns].copy(),
    }


def build_customer_crosswalk(
    customer_masters: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    records = []

    unique_counter = (
        SHARED_CUSTOMER_GROUPS + 1
    )

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:

        df = (
            customer_masters[country_code]
            .sort_values(
                "local_customer_id"
            )
            .reset_index(drop=True)
        )

        for index, row in df.iterrows():

            if index < SHARED_CUSTOMER_GROUPS:

                regional_customer_id = (
                    f"RCUST-{index + 1:05d}"
                )

                mapping_type = (
                    "SYNTHETIC_REGIONAL_GROUP"
                )

            else:

                regional_customer_id = (
                    f"RCUST-{unique_counter:05d}"
                )

                unique_counter += 1

                mapping_type = (
                    "SYNTHETIC_LOCAL_ONLY"
                )

            records.append(
                {
                    "source_country":
                        country_code,

                    "local_customer_id":
                        row[
                            "local_customer_id"
                        ],

                    "regional_customer_id":
                        regional_customer_id,

                    "mapping_type":
                        mapping_type,

                    "mapping_status":
                        "APPROVED_SYNTHETIC",

                    "mapping_source":
                        "PORTFOLIO_MASTER_DATA_RULE",

                    "effective_from":
                        "2024-09-01",

                    "effective_to":
                        None,
                }
            )

    crosswalk = pd.DataFrame(
        records
    )

    return crosswalk


def build_supplier_crosswalk(
    supplier_masters: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    records = []

    unique_counter = (
        SHARED_SUPPLIER_GROUPS + 1
    )

    for country_code in [
        "MY",
        "SG",
        "ID",
    ]:

        df = (
            supplier_masters[
                country_code
            ]
            .sort_values(
                "local_supplier_id"
            )
            .reset_index(drop=True)
        )

        for index, row in df.iterrows():

            if index < SHARED_SUPPLIER_GROUPS:

                regional_supplier_id = (
                    f"RSUP-{index + 1:05d}"
                )

                mapping_type = (
                    "SYNTHETIC_REGIONAL_GROUP"
                )

            else:

                regional_supplier_id = (
                    f"RSUP-{unique_counter:05d}"
                )

                unique_counter += 1

                mapping_type = (
                    "SYNTHETIC_LOCAL_ONLY"
                )

            records.append(
                {
                    "source_country":
                        country_code,

                    "local_supplier_id":
                        row[
                            "local_supplier_id"
                        ],

                    "regional_supplier_id":
                        regional_supplier_id,

                    "mapping_type":
                        mapping_type,

                    "mapping_status":
                        "APPROVED_SYNTHETIC",

                    "mapping_source":
                        "PORTFOLIO_MASTER_DATA_RULE",

                    "effective_from":
                        "2024-09-01",

                    "effective_to":
                        None,
                }
            )

    return pd.DataFrame(
        records
    )


def build_customer_dimension(
    customer_masters: dict[str, pd.DataFrame],
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:

    local_frames = []

    for country_code, df in (
        customer_masters.items()
    ):

        country_df = df.copy()

        country_df[
            "source_country"
        ] = country_code

        local_frames.append(
            country_df
        )

    local_customers = pd.concat(
        local_frames,
        ignore_index=True,
    )

    mastered = local_customers.merge(
        crosswalk,
        on=[
            "source_country",
            "local_customer_id",
        ],
        how="left",
        validate="one_to_one",
    )

    summary = (
        mastered.groupby(
            "regional_customer_id",
            as_index=False,
        )
        .agg(
            local_entity_count=(
                "local_customer_id",
                "nunique",
            ),
            country_count=(
                "source_country",
                "nunique",
            ),
            primary_industry=(
                "industry",
                lambda x:
                    x.dropna().iloc[0]
                    if not x.dropna().empty
                    else None,
            ),
            primary_segment=(
                "customer_segment",
                lambda x:
                    x.dropna().iloc[0]
                    if not x.dropna().empty
                    else None,
            ),
        )
    )

    summary[
        "regional_customer_name"
    ] = summary[
        "regional_customer_id"
    ].apply(
        lambda value:
            f"Synthetic Corporate Group "
            f"{value.replace('RCUST-', '')}"
    )

    summary[
        "customer_scope"
    ] = summary[
        "country_count"
    ].apply(
        lambda value:
            "MULTI_COUNTRY"
            if value > 1
            else "LOCAL_ONLY"
    )

    selected_columns = [
        "regional_customer_id",
        "regional_customer_name",
        "customer_scope",
        "local_entity_count",
        "country_count",
        "primary_segment",
        "primary_industry",
    ]

    return summary[
        selected_columns
    ]


def build_supplier_dimension(
    supplier_masters: dict[str, pd.DataFrame],
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:

    local_frames = []

    for country_code, df in (
        supplier_masters.items()
    ):

        country_df = df.copy()

        country_df[
            "source_country"
        ] = country_code

        local_frames.append(
            country_df
        )

    local_suppliers = pd.concat(
        local_frames,
        ignore_index=True,
    )

    mastered = local_suppliers.merge(
        crosswalk,
        on=[
            "source_country",
            "local_supplier_id",
        ],
        how="left",
        validate="one_to_one",
    )

    summary = (
        mastered.groupby(
            "regional_supplier_id",
            as_index=False,
        )
        .agg(
            local_entity_count=(
                "local_supplier_id",
                "nunique",
            ),
            country_count=(
                "source_country",
                "nunique",
            ),
            primary_supplier_type=(
                "supplier_type",
                lambda x:
                    x.dropna().iloc[0]
                    if not x.dropna().empty
                    else None,
            ),
        )
    )

    summary[
        "regional_supplier_name"
    ] = summary[
        "regional_supplier_id"
    ].apply(
        lambda value:
            f"Synthetic Supplier Group "
            f"{value.replace('RSUP-', '')}"
    )

    summary[
        "supplier_scope"
    ] = summary[
        "country_count"
    ].apply(
        lambda value:
            "MULTI_COUNTRY"
            if value > 1
            else "LOCAL_ONLY"
    )

    selected_columns = [
        "regional_supplier_id",
        "regional_supplier_name",
        "supplier_scope",
        "local_entity_count",
        "country_count",
        "primary_supplier_type",
    ]

    return summary[
        selected_columns
    ]


def validate_customer_crosswalk(
    crosswalk: pd.DataFrame,
) -> None:

    duplicate_local_keys = (
        crosswalk.duplicated(
            subset=[
                "source_country",
                "local_customer_id",
            ],
            keep=False,
        )
        .sum()
    )

    if duplicate_local_keys > 0:

        raise RuntimeError(
            "Customer crosswalk has "
            f"{duplicate_local_keys} "
            "duplicate local keys."
        )

    if (
        crosswalk[
            "regional_customer_id"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Customer crosswalk contains "
            "unmapped regional IDs."
        )


def validate_supplier_crosswalk(
    crosswalk: pd.DataFrame,
) -> None:

    duplicate_local_keys = (
        crosswalk.duplicated(
            subset=[
                "source_country",
                "local_supplier_id",
            ],
            keep=False,
        )
        .sum()
    )

    if duplicate_local_keys > 0:

        raise RuntimeError(
            "Supplier crosswalk has "
            f"{duplicate_local_keys} "
            "duplicate local keys."
        )

    if (
        crosswalk[
            "regional_supplier_id"
        ]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "Supplier crosswalk contains "
            "unmapped regional IDs."
        )


def main() -> None:

    REFERENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    customer_masters = (
        load_customer_masters()
    )

    supplier_masters = (
        load_supplier_masters()
    )

    customer_crosswalk = (
        build_customer_crosswalk(
            customer_masters
        )
    )

    supplier_crosswalk = (
        build_supplier_crosswalk(
            supplier_masters
        )
    )

    validate_customer_crosswalk(
        customer_crosswalk
    )

    validate_supplier_crosswalk(
        supplier_crosswalk
    )

    customer_dimension = (
        build_customer_dimension(
            customer_masters,
            customer_crosswalk,
        )
    )

    supplier_dimension = (
        build_supplier_dimension(
            supplier_masters,
            supplier_crosswalk,
        )
    )

    customer_crosswalk.to_csv(
        REFERENCE_DIR
        / "customer_crosswalk.csv",
        index=False,
    )

    supplier_crosswalk.to_csv(
        REFERENCE_DIR
        / "supplier_crosswalk.csv",
        index=False,
    )

    customer_dimension.to_parquet(
        SILVER_DIR
        / "dim_customer_master.parquet",
        index=False,
    )

    supplier_dimension.to_parquet(
        SILVER_DIR
        / "dim_supplier_master.parquet",
        index=False,
    )

    print(
        "\nRegional master-data build completed."
    )

    print(
        "\nCustomer crosswalk:"
    )

    print(
        f"Local customer entities: "
        f"{len(customer_crosswalk):,}"
    )

    print(
        f"Regional customers: "
        f"{customer_crosswalk['regional_customer_id'].nunique():,}"
    )

    print(
        f"Multi-country customers: "
        f"{(customer_dimension['country_count'] > 1).sum():,}"
    )

    print(
        "\nSupplier crosswalk:"
    )

    print(
        f"Local supplier entities: "
        f"{len(supplier_crosswalk):,}"
    )

    print(
        f"Regional suppliers: "
        f"{supplier_crosswalk['regional_supplier_id'].nunique():,}"
    )

    print(
        f"Multi-country suppliers: "
        f"{(supplier_dimension['country_count'] > 1).sum():,}"
    )


if __name__ == "__main__":
    main()