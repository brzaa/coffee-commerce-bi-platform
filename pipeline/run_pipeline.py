from __future__ import annotations

import os
import subprocess

from prefect import flow, task

from pipeline.generate_synthetic_data import generate_dataset
from pipeline.load_raw import load_raw_data
from pipeline.settings import ANALYTICS_DIR, DATA_DIR


@task(log_prints=True)
def generate_sources() -> str:
    return str(generate_dataset(DATA_DIR))


@task(log_prints=True)
def load_raw_sources() -> None:
    load_raw_data(DATA_DIR)


@task(log_prints=True)
def run_dbt_build() -> None:
    env = os.environ.copy()
    env.setdefault("DBT_PROFILES_DIR", str(ANALYTICS_DIR))
    subprocess.run(
        ["dbt", "build", "--project-dir", str(ANALYTICS_DIR), "--profiles-dir", str(ANALYTICS_DIR)],
        check=True,
        env=env,
    )


@flow(name="coffee-commerce-bi-refresh")
def coffee_commerce_bi_pipeline() -> None:
    generate_sources()
    load_raw_sources()
    run_dbt_build()


if __name__ == "__main__":
    coffee_commerce_bi_pipeline()
