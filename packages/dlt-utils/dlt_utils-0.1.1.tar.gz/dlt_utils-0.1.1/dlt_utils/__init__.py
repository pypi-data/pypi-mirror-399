"""
dlt_utils: Shared utilities for dlt data pipelines with multi-company support.

This package provides common utilities for building dlt pipelines that work with
multiple companies/tenants, including:

- PartitionedIncremental: State tracking per partition key
- Date utilities: Generate (year, week) and (year, month) sequences
- Schema utilities: Ensure database tables exist
- CLI argument parsing with standard arguments
- Logging configuration
- Pipeline helpers
"""

from .incremental import PartitionedIncremental
from .dates import generate_year_weeks, generate_year_months
from .schema import (
    ensure_all_tables_exist,
    ensure_tables_for_resources,
    get_tables_for_resources,
)
from .args import (
    add_common_args,
    create_base_parser,
    CommonArgs,
)
from .logging import configure_logging
from .pipeline import (
    validate_refresh_args,
    filter_resources,
    print_resources,
)


__version__ = "0.1.1"

__all__ = [
    # Incremental
    "PartitionedIncremental",
    # Dates
    "generate_year_weeks",
    "generate_year_months",
    # Schema
    "ensure_all_tables_exist",
    "ensure_tables_for_resources",
    "get_tables_for_resources",
    # args
    "add_common_args",
    "create_base_parser",
    "CommonArgs",
    # logging
    "configure_logging",
    # pipeline
    "validate_refresh_args",
    "filter_resources",
    "print_resources",
]
