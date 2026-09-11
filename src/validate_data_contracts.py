from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pandera.pandas as pa
import yaml
from pandera import Check, Column, DataFrameSchema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = PROJECT_ROOT / "config" / "data_contracts.yml"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "data_contracts"


def load_contracts() -> dict[str, Any]:
    with CONTRACT_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_dataset(
    relative_path: str,
    file_format: str,
) -> pd.DataFrame:
    path = PROJECT_ROOT / relative_path

    if file_format == "csv":
        return pd.read_csv(path)

    if file_format == "excel":
        return pd.read_excel(path)

    raise ValueError(
        f"Unsupported file format: {file_format}"
    )


def pandera_dtype(dtype_name: str):
    mapping = {
        "string": pa.String,
        "float": pa.Float,
        "integer": pa.Int,
        "datetime": pa.DateTime,
        "boolean": pa.Bool,
    }

    if dtype_name not in mapping:
        raise ValueError(
            f"Unsupported contract dtype: {dtype_name}"
        )

    return mapping[dtype_name]


def build_column_schema(
    column_config: dict[str, Any],
) -> Column:
    checks = []

    allowed_values = column_config.get(
        "allowed_values"
    )

    if allowed_values is not None:
        checks.append(
            Check.isin(
                allowed_values
            )
        )

    minimum = column_config.get(
        "minimum"
    )

    if minimum is not None:
        checks.append(
            Check.ge(
                minimum
            )
        )

    maximum = column_config.get(
        "maximum"
    )

    if maximum is not None:
        checks.append(
            Check.le(
                maximum
            )
        )

    return Column(
        pandera_dtype(
            column_config["dtype"]
        ),
        nullable=column_config.get(
            "nullable",
            False,
        ),
        checks=checks,
        coerce=True,
        required=True,
    )


def build_schema(
    dataset_config: dict[str, Any],
) -> DataFrameSchema:
    columns = {}

    for column_name, column_config in (
        dataset_config[
            "required_columns"
        ].items()
    ):
        columns[column_name] = (
            build_column_schema(
                column_config
            )
        )

    primary_key = dataset_config.get(
        "primary_key"
    )

    dataframe_checks = []

    if primary_key:
        dataframe_checks.append(
            Check(
                lambda df: (
                    ~df[
                        primary_key
                    ].duplicated()
                ).all(),
                error=(
                    f"Primary key "
                    f"{primary_key} "
                    f"must be unique"
                ),
            )
        )

    return DataFrameSchema(
        columns=columns,
        checks=dataframe_checks,
        strict=False,
        coerce=True,
    )


def validate_dataset(
    dataset_name: str,
    dataset_config: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    dataframe = load_dataset(
        relative_path=dataset_config[
            "file"
        ],
        file_format=dataset_config[
            "format"
        ],
    )

    schema = build_schema(
        dataset_config
    )

    summary = {
        "dataset_name": dataset_name,
        "country_code": dataset_config[
            "country_code"
        ],
        "file": dataset_config[
            "file"
        ],
        "row_count": len(dataframe),
        "status": "PASS",
        "failure_count": 0,
    }

    failures = pd.DataFrame()

    try:
        schema.validate(
            dataframe,
            lazy=True,
        )

    except pa.errors.SchemaErrors as error:
        summary[
            "status"
        ] = "FAIL"

        failures = (
            error.failure_cases.copy()
        )

        summary[
            "failure_count"
        ] = len(failures)

        failures.insert(
            0,
            "dataset_name",
            dataset_name,
        )

        failures.insert(
            1,
            "country_code",
            dataset_config[
                "country_code"
            ],
        )

    return summary, failures


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    contracts = load_contracts()

    summaries = []
    failure_frames = []

    for dataset_name, dataset_config in (
        contracts[
            "datasets"
        ].items()
    ):
        print(
            f"Validating contract: "
            f"{dataset_name}"
        )

        summary, failures = (
            validate_dataset(
                dataset_name,
                dataset_config,
            )
        )

        summaries.append(
            summary
        )

        if not failures.empty:
            failure_frames.append(
                failures
            )

    summary_df = pd.DataFrame(
        summaries
    )

    summary_df.to_csv(
        OUTPUT_DIR
        / "contract_validation_summary.csv",
        index=False,
    )

    if failure_frames:
        failure_df = pd.concat(
            failure_frames,
            ignore_index=True,
        )

        failure_df.to_csv(
            OUTPUT_DIR
            / "contract_validation_failures.csv",
            index=False,
        )

    else:
        failure_df = pd.DataFrame()

    print(
        "\nContract validation summary:"
    )

    print(
        summary_df.to_string(
            index=False
        )
    )

    if not failure_df.empty:
        print(
            "\nFailure cases detected."
        )

        display_columns = [
            column
            for column in [
                "dataset_name",
                "country_code",
                "schema_context",
                "column",
                "check",
                "failure_case",
                "index",
            ]
            if column
            in failure_df.columns
        ]

        print(
            failure_df[
                display_columns
            ]
            .head(50)
            .to_string(
                index=False
            )
        )

    else:
        print(
            "\nAll contracts passed."
        )


if __name__ == "__main__":
    main()