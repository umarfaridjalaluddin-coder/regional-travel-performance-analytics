from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.json"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_country_reference(config: dict) -> pd.DataFrame:
    records = []

    for country_code, values in config["countries"].items():
        records.append(
            {
                "country_code": country_code,
                "country_name": values["country_name"],
                "region": "Southeast Asia",
                "local_currency": values["local_currency"],
                "reporting_currency": config["reporting_currency"],
            }
        )

    return pd.DataFrame(records)


def create_product_mapping() -> pd.DataFrame:
    mappings = [
        # Malaysia
        ("MY", "Air", "Air"),
        ("MY", "Hotel", "Hotel"),
        ("MY", "Ground", "Ground"),
        ("MY", "Other", "Other"),

        # Singapore
        ("SG", "Flight", "Air"),
        ("SG", "Accommodation", "Hotel"),
        ("SG", "Transport", "Ground"),
        ("SG", "Other Service", "Other"),

        # Indonesia
        ("ID", "AIR", "Air"),
        ("ID", "HOTEL", "Hotel"),
        ("ID", "GROUND", "Ground"),
        ("ID", "OTHER", "Other"),
    ]

    return pd.DataFrame(
        mappings,
        columns=[
            "country_code",
            "source_product",
            "regional_product",
        ],
    )


def create_channel_mapping() -> pd.DataFrame:
    mappings = [
        # Malaysia
        ("MY", "Online", "Online"),
        ("MY", "Offline", "Offline"),

        # Singapore
        ("SG", "OBT", "Online"),
        ("SG", "Agent", "Offline"),

        # Indonesia
        ("ID", "ONLINE", "Online"),
        ("ID", "MANUAL", "Offline"),
    ]

    return pd.DataFrame(
        mappings,
        columns=[
            "country_code",
            "source_channel",
            "regional_channel",
        ],
    )


def create_currency_reference(config: dict) -> pd.DataFrame:
    """
    Generate synthetic monthly FX rates to MYR.

    These rates are fictional and exist only for the portfolio case study.
    """

    rng = np.random.default_rng(config["random_seed"])

    months = pd.date_range(
        start=config["start_date"],
        end=config["end_date"],
        freq="MS",
    )

    # Synthetic starting assumptions only.
    base_rates = {
        "MYR": 1.0,
        "SGD": 3.45,
        "IDR": 0.00029,
    }

    records = []

    for currency_code, base_rate in base_rates.items():
        current_rate = base_rate

        for month in months:
            if currency_code == "MYR":
                current_rate = 1.0
            else:
                monthly_change = rng.normal(loc=0.0, scale=0.01)
                current_rate *= 1 + monthly_change

            records.append(
                {
                    "effective_month": month.date(),
                    "currency_code": currency_code,
                    "reporting_currency": config["reporting_currency"],
                    "rate_to_reporting_currency": round(current_rate, 8),
                    "rate_type": "synthetic_monthly",
                }
            )

    return pd.DataFrame(records)


def save_dataframe(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    output_path = REFERENCE_DIR / filename
    dataframe.to_csv(output_path, index=False)

    print(
        f"Created {output_path.relative_to(PROJECT_ROOT)} "
        f"({len(dataframe):,} rows)"
    )


def main() -> None:
    config = load_config()

    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    country_reference = create_country_reference(config)
    product_mapping = create_product_mapping()
    channel_mapping = create_channel_mapping()
    currency_reference = create_currency_reference(config)

    save_dataframe(
        country_reference,
        "country_reference.csv",
    )

    save_dataframe(
        product_mapping,
        "product_mapping.csv",
    )

    save_dataframe(
        channel_mapping,
        "channel_mapping.csv",
    )

    save_dataframe(
        currency_reference,
        "currency_reference.csv",
    )

    print("\nReference-data generation completed successfully.")


if __name__ == "__main__":
    main()