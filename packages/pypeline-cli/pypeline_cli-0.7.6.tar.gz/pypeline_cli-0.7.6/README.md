# pypeline-cli

> **A highly-opinionated, batteries-included lightweight framework for building Snowflake ETL pipelines with Snowpark.**
>
> pypeline-cli scaffolds production-ready data pipeline projects with built-in session management, logging, table configuration, and a proven Extract-Transform-Load pattern - allowing developers to focus on business logic while the framework handles infrastructure and best practices.

[![PyPI version](https://badge.fury.io/py/pypeline-cli.svg)](https://badge.fury.io/py/pypeline-cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Why pypeline-cli?](#why-pypeline-cli)
- [Philosophy](#philosophy)
- [Features](#features)
- [Installation](#installation)
- [Quick Start Tutorial](#quick-start-tutorial)
- [Command Reference](#command-reference)
- [Project Structure](#project-structure)
- [Example Generated Structures](#example-generated-structures)
- [Development Workflow](#development-workflow)
- [ETL Architecture & Best Practices](#etl-architecture--best-practices)
- [Built-in Utilities](#built-in-utilities)
- [Requirements](#requirements)
- [Contributing](#contributing)

---

## Why pypeline-cli?

### The Problem

Building production data pipelines in Snowflake involves repetitive boilerplate:
- Setting up project structure with proper src-layout
- Configuring Snowpark sessions and managing connections
- Writing table configuration logic for time-partitioned tables
- Implementing logging, timing, and monitoring
- Managing dependencies across multiple files
- Structuring Extract-Transform-Load (ETL) logic consistently

**This takes time away from what matters: your business logic.**

### The Solution

pypeline-cli generates opinionated, production-ready project structures that follow industry best practices. It provides:

✅ **Instant scaffolding** - Complete project setup in seconds

✅ **Consistent architecture** - Processor pattern for modular ETL logic

✅ **Built-in utilities** - Logger, ETL singleton, decorators, table configs

✅ **Dependency management** - User-friendly Python file instead of TOML editing

✅ **Snowflake-first** - Designed specifically for Snowpark development

---

## Philosophy

pypeline-cli is built on several core principles that guide how data pipelines are structured and organized:

### 1. **Convention Over Configuration**
Projects follow a standardized structure. This means:
- Onboarding new team members is faster
- Code reviews focus on business logic, not project setup
- Switching between projects feels familiar

### 2. **Separation of Concerns**
Clear boundaries between different pipeline components:

- **Processors** - A processor is a cohesive group of **atomized transformations**. Each processor:
  - Receives pre-loaded data via TableCache (Extract is done at pipeline level)
  - Orchestrates transformations in `process()` (Transform phase)
  - Contains private methods that perform single, focused transformations
  - Represents a logical unit of work (e.g., "enrich customer data", "calculate metrics")
  - Returns a transformed DataFrame ready for the next stage

- **Pipelines** - A pipeline is an **organized sequence of processors**. Each pipeline:
  - **Handles Extract**: Pre-loads all input tables into TableCache in `__init__()`
  - **Orchestrates Transform**: Instantiates processors with shared cache, chains transformations
  - **Handles Load**: Writes final output via `_write_to_snowflake()`
  - Manages the high-level workflow and business logic
  - Provides conditional write logic with the `_write` flag

- **Utilities** - Framework-provided tools that handle cross-cutting concerns:
  - **ETL Singleton**: Manages Snowpark session lifecycle
  - **Logger**: Structured, color-coded logging with context
  - **TableConfig**: Dynamic table naming with time-based partitioning
  - **TableCache**: Pre-loads and caches input tables for efficiency
  - **Decorators**: Performance timing, table existence checks, freshness validation
  - **Databases/Schemas**: Centralized constants for environment configuration

- **Config** - Configuration files that centralize definitions:
  - **databases.py**: Database and schema name constants
  - **tables.py**: TableConfig instances for all data sources
  - **columns.py**: Column generation utilities for dynamic schemas
  - **Pipeline config.py**: Pipeline-specific table configurations

**The Core Pattern:**
```
Pipeline.__init__()
    ↓
Extract: Pre-load all input tables into TableCache
    ↓
Processor 1(cache)
    ↓
Transform: Access cached tables, apply atomized transformations
    ↓
Processor 2(cache)
    ↓
Transform: Further transformations, aggregations
    ↓
Processor 3(cache)
    ↓
Transform: Final transformations
    ↓
Pipeline._write_to_snowflake()
    ↓
Load: Write final DataFrame to Snowflake
```

**Key Insight:** Extract happens **once** at the pipeline level (via TableCache). Each processor receives the pre-loaded cache and focuses purely on **Transform** logic. This eliminates redundant queries and ensures all processors work with identical data snapshots.

### 3. **Developer Experience First**
- Edit dependencies in Python, not TOML
- Automatic import registration for pipelines and processors
- CLI-driven scaffolding reduces copy-paste errors
- Framework files marked "DO NOT MODIFY" for clarity
- User-editable files clearly documented
- Auto-generated test scaffolding with pytest fixtures

### 4. **Production-Ready from Day One**
- Singleton ETL pattern prevents session leaks
- Structured logging with context and timestamps
- Performance timing decorators built-in
- Git integration and proper versioning (hatch-vcs)
- TableCache pattern reduces redundant Snowflake queries
- Comprehensive error handling and validation

---

## Features

### 🚀 **Project Scaffolding**
- Generate complete pipeline projects in seconds
- Pre-configured with Snowpark, logging, and utilities
- Git initialization with proper configuration

### 📦 **Smart Dependency Management**
- Edit dependencies in a simple Python list
- Automatic synchronization to `pyproject.toml`
- Validation of version specifications

### 🏗️ **Pipeline & Processor Generation**
- Create pipelines with `pypeline create-pipeline`
- Create processors with `pypeline create-processor`
- Auto-registration for top-level imports

### 🔧 **Built-in Utilities**
- **ETL singleton** for Snowpark session management
- **Logger** with color-coded levels and context
- **Decorators** for timing, table existence checks, freshness validation
- **TableConfig** for dynamic table naming (yearly, monthly, stable)

### 🎯 **Opinionated Templates**
- Processor pattern: Extract in `__init__`, Transform in `process()`
- Pipeline pattern: Orchestrate processors, conditional writes
- Test scaffolding with pytest fixtures

---

## Installation

### Using pip (Recommended)

```bash
pip install pypeline-cli
```

### From Source

```bash
git clone https://github.com/dbrown540/pypeline-cli.git
cd pypeline-cli
pipx install -e .
```

---

## Quick Start Tutorial

This tutorial will walk you through creating your first data pipeline from scratch.

### Step 1: Initialize a New Project

```bash
pypeline init \
  --name customer_analytics \
  --author-name "Jane Doe" \
  --author-email "jane@company.com" \
  --description "Customer analytics data pipelines" \
  --license mit
```

**What this creates:**
- Complete project structure (flat package layout)
- Git repository with initial commit
- `pyproject.toml` configured for Python 3.12+
- Utility modules (ETL, Logger, TableConfig, etc.)
- Dependencies file for easy package management

### Step 2: Navigate and Install Dependencies

```bash
cd customer_analytics
pypeline install
```

This creates a `.venv` virtual environment and installs all dependencies.

### Step 3: Configure Your Databases and Tables

Edit `customer_analytics/utils/databases.py`:

```python
class Database:
    RAW = "RAW_DATA"
    STAGING = "STAGING"
    PROD = "PRODUCTION"

class Schema:
    LANDING = "LANDING_ZONE"
    TRANSFORM = "TRANSFORMED"
    ANALYTICS = "ANALYTICS"
```

Edit `customer_analytics/utils/tables.py`:

```python
from .databases import Database, Schema

# Example: Monthly partitioned sales table
SALES_MONTHLY = TableConfig(
    database=Database.RAW,
    schema=Schema.LANDING,
    table_name_template="sales_{MM}",
    type="MONTHLY",
    month=1  # Can be updated dynamically
)

# Example: Yearly customer dimension
CUSTOMER_DIM = TableConfig(
    database=Database.PROD,
    schema=Schema.ANALYTICS,
    table_name_template="dim_customer_{YYYY}",
    type="YEARLY"
)

# Example: Stable reference table
PRODUCT_REF = TableConfig(
    database=Database.PROD,
    schema=Schema.ANALYTICS,
    table_name_template="ref_products",
    type="STABLE"
)
```

### Step 4: Create Your First Pipeline

```bash
pypeline create-pipeline --name customer-segmentation
```

**What this creates:**
```
customer_analytics/pipelines/customer_segmentation/
├── __init__.py                        # Package marker
├── customer_segmentation_runner.py   # Main orchestrator
├── config.py                          # Pipeline-specific config
├── README.md                          # Documentation
├── processors/                        # Processor classes go here
│   └── __init__.py
└── tests/                             # Integration tests
    └── __init__.py
```

The pipeline is automatically registered in your package's `__init__.py`, allowing:
```python
from customer_analytics import CustomerSegmentationPipeline
```

### Step 5: Configure Pipeline Tables

Before creating processors, define your table configurations in `customer_analytics/pipelines/customer_segmentation/config.py`:

```python
from ..utils.tables import TableConfig
from ..utils.databases import Database, Schema

# Define all tables used by this pipeline
TABLE_CONFIGS = {
    # Input tables (will be pre-loaded into cache)
    "sales": TableConfig(
        database=Database.RAW,
        schema=Schema.LANDING,
        table_name_template="sales_{MM}",
        type="MONTHLY",
        month=1,  # Will be set dynamically
        is_output=False
    ),
    "customers": TableConfig(
        database=Database.PROD,
        schema=Schema.DIM,
        table_name_template="dim_customers",
        type="STABLE",
        is_output=False
    ),
    # Output table (not pre-loaded)
    "output": TableConfig(
        database=Database.PROD,
        schema=Schema.ANALYTICS,
        table_name_template="customer_segments_{MM}",
        type="MONTHLY",
        month=1,
        is_output=True
    )
}
```

### Step 6: Create Processors

Create a processor for each transformation concern:

```bash
pypeline create-processor --name sales-transformer --pipeline customer-segmentation
pypeline create-processor --name customer-enrichment --pipeline customer-segmentation
pypeline create-processor --name segmentation-logic --pipeline customer-segmentation
```

Each processor is scaffolded with:
- `__init__(cache)` method that receives pre-loaded TableCache
- `process()` method for transformations
- Logger and ETL utilities auto-instantiated
- Unit test file with pytest fixtures

### Step 7: Implement Processor Logic

Edit `customer_analytics/pipelines/customer_segmentation/processors/sales_transformer_processor.py`:

```python
from typing import Final
from snowflake.snowpark import DataFrame
from snowflake.snowpark.functions import col, sum_ as sum_, count

from ....utils.logger import Logger
from ....utils.decorators import time_function

MODULE_NAME: Final[str] = "pipelines/customer_segmentation/processors/sales_transformer_processor.py"


class SalesTransformerProcessor:
    """
    Transforms sales data from pre-loaded cache.

    This processor accesses pre-loaded sales and customer data from the cache
    and performs transformations to prepare data for segmentation.
    """

    def __init__(self, cache: Dict[str, DataFrame]):
        """
        Initialize with pre-populated cache from pipeline.

        Args:
            cache: TableCache with pre-loaded input tables
        """
        self.logger = Logger()
        self.cache = cache

        # Access pre-loaded tables from cache (no Snowflake query)
        self.sales_df = cache.get_table("sales")
        self.customers_df = cache.get_table("customers")

        self.logger.info(
            message="Initialized SalesTransformerProcessor with cached tables",
            context=MODULE_NAME
        )

    @time_function(f"{MODULE_NAME}.process")
    def process(self) -> DataFrame:
        """
        Transform sales data: filter, aggregate, and prepare for enrichment.

        Returns:
            Transformed DataFrame with customer purchase metrics
        """
        self.logger.info(
            message="Starting sales data transformation",
            context=MODULE_NAME
        )

        # Apply transformations using cached data
        df = self._filter_valid_transactions()
        df = self._aggregate_by_customer(df)
        df = self._enrich_with_customer_info(df)
        df = self._calculate_metrics(df)

        return df

    def _filter_valid_transactions(self) -> DataFrame:
        """
        Filter out invalid or cancelled transactions.

        Returns:
            Filtered DataFrame
        """
        return self.sales_df.filter(
            (col("STATUS") == "COMPLETED") &
            (col("AMOUNT") > 0)
        )

    def _aggregate_by_customer(self, df: DataFrame) -> DataFrame:
        """
        Aggregate sales metrics by customer.

        Args:
            df: Filtered sales DataFrame

        Returns:
            DataFrame with customer-level aggregates
        """
        return df.group_by("CUSTOMER_ID").agg(
            sum_("AMOUNT").alias("TOTAL_SALES"),
            count("TRANSACTION_ID").alias("TRANSACTION_COUNT")
        )

    def _enrich_with_customer_info(self, df: DataFrame) -> DataFrame:
        """
        Join with customer data from cache.

        Args:
            df: Aggregated sales DataFrame

        Returns:
            DataFrame enriched with customer information
        """
        # Use pre-loaded customer data (no additional query)
        return df.join(
            self.customers_df.select("CUSTOMER_ID", "CUSTOMER_TIER", "REGION"),
            on="CUSTOMER_ID",
            how="left"
        )

    def _calculate_metrics(self, df: DataFrame) -> DataFrame:
        """
        Calculate derived metrics like average order value.

        Args:
            df: Enriched DataFrame

        Returns:
            DataFrame with calculated metrics
        """
        return df.with_column(
            "AVG_ORDER_VALUE",
            col("TOTAL_SALES") / col("TRANSACTION_COUNT")
        )
```

### Step 8: Wire Processors in Pipeline Runner

Edit `customer_analytics/pipelines/customer_segmentation/customer_segmentation_runner.py`:

```python
from pathlib import Path
from typing import Final, Literal

from snowflake.snowpark import DataFrame

from ...utils.etl import ETL
from ...utils.logger import Logger
from ...utils.decorators import time_function
from ...utils.table_cache import TableCache
from .config import TABLE_CONFIGS

# Import processors (auto-added by create-processor command)
from .processors.sales_transformer_processor import SalesTransformerProcessor
from .processors.customer_enrichment_processor import CustomerEnrichmentProcessor
from .processors.segmentation_logic_processor import SegmentationLogicProcessor

MODULE_NAME: Final[str] = Path(__file__).name


class CustomerSegmentationPipeline:
    """
    Customer segmentation pipeline.

    Pre-loads sales and customer data, applies transformations through processors,
    and writes customer segments to Snowflake.
    """

    def __init__(self, month: int):
        """
        Initialize pipeline, pre-load all input tables, and instantiate processors.

        Args:
            month: Month to process (1-12)
        """
        self.logger = Logger()
        self.etl = ETL()
        self.month = month

        # Update month in table configs
        TABLE_CONFIGS["sales"].month = month
        TABLE_CONFIGS["output"].month = month

        # EXTRACT: Pre-load all input tables into cache (one-time operation)
        self.cache = TableCache().preload_tables(
            table_keys=[k for k, config in TABLE_CONFIGS.items() if not config.is_output],
            table_configs=TABLE_CONFIGS
        )

        self.logger.info(
            message=f"Pre-loaded {len(self.cache.tables)} input tables into cache",
            context=MODULE_NAME
        )

        # Instantiate all processors with shared cache (auto-registered)
        self.sales_transformer = SalesTransformerProcessor(self.cache)
        self.customer_enrichment = CustomerEnrichmentProcessor(self.cache)
        self.segmentation_logic = SegmentationLogicProcessor(self.cache)

    @time_function("CustomerSegmentationPipeline.run")
    def run(self, _write: bool = False):
        """
        Entry point for pipeline execution.

        Args:
            _write: If True, writes results to Snowflake
        """
        self.pipeline(_write)
        self.logger.info(
            message="Customer segmentation pipeline completed successfully.",
            context=MODULE_NAME,
        )

    def pipeline(self, _write: bool):
        """
        Orchestrate processor execution and write logic.

        Args:
            _write: If True, writes results to Snowflake
        """
        # TRANSFORM: Run processors with shared cache
        df: DataFrame = self.run_processors()

        # LOAD: Conditionally write to Snowflake
        if _write:
            output_config = TABLE_CONFIGS["output"]
            table_path = output_config.generate_table_name()
            self._write_to_snowflake(df, write_mode="overwrite", table_path=table_path)

    def run_processors(self) -> DataFrame:
        """
        Execute processors in sequence using pre-instantiated processor instances.

        Returns:
            Final DataFrame with customer segments
        """
        # Use pre-instantiated processors from __init__
        sales_df = self.sales_transformer.process()
        enriched_df = self.customer_enrichment.process(sales_df)
        segmented_df = self.segmentation_logic.process(enriched_df)

        return segmented_df

    def _write_to_snowflake(
        self,
        df: DataFrame,
        write_mode: Literal["append", "overwrite", "truncate"],
        table_path: str,
    ):
        """
        Write DataFrame to Snowflake table.

        Args:
            df: DataFrame to write
            write_mode: Write mode for save_as_table
            table_path: Fully qualified table name
        """
        self.logger.info(
            message=f"Writing DataFrame to {table_path}",
            context=MODULE_NAME
        )

        df.write.mode(write_mode).save_as_table(table_path)

        self.logger.info(
            message=f"Successfully saved table to {table_path}",
            context=MODULE_NAME
        )


if __name__ == "__main__":
    pipeline = CustomerSegmentationPipeline(month=3)
    pipeline.run(_write=True)
```

### Step 9: Build for Snowflake Deployment

Build a Snowflake-compatible ZIP archive of your project:

```bash
# From project root
pypeline build
```

**Output:**
```
dist/
└── snowflake/
    └── customer_analytics-0.1.0.zip
```

The build command:
- Creates a ZIP with `pyproject.toml` at root level (required by Snowflake)
- Includes your package and all dependencies configuration
- Excludes build artifacts, virtual environments, and cache files
- Verifies the structure is Snowflake-compatible

You can now upload this ZIP to a Snowflake stage and use it in stored procedures or UDFs.

---

## Command Reference

### `pypeline init`

Creates a new pypeline project with complete structure.

**Usage:**
```bash
pypeline init \
  --name my-pipeline \
  --author-name "Your Name" \
  --author-email "you@example.com" \
  --description "Pipeline description" \
  --license mit
```

**Options:**
- `--destination PATH` - Where to create project (default: current directory)
- `--name TEXT` - Project name (required, must be valid Python identifier)
- `--author-name TEXT` - Author name (required)
- `--author-email TEXT` - Author email (required)
- `--description TEXT` - Project description (required)
- `--license TEXT` - License type (required)
  - Available: `mit`, `apache-2.0`, `gpl-3.0`, `gpl-2.0`, `lgpl-2.1`, `bsd-2-clause`, `bsd-3-clause`, `bsl-1.0`, `cc0-1.0`, `epl-2.0`, `agpl-3.0`, `mpl-2.0`, `unlicense`, `proprietary`
- `--company-name TEXT` - Company/organization name (optional, for license)
- `--git / --no-git` - Initialize git repository (default: disabled)

**What it creates:**

Complete project scaffolding:

```
my_pipeline/
├── pyproject.toml                   # Package configuration
│                                    # - Git-based versioning (if --git)
│                                    # - Manual version "0.1.0" (if --no-git)
├── dependencies.py                  # ✏️ User-editable dependency list
├── LICENSE                          # Selected license file
├── README.md                        # Project documentation template
├── .gitignore                       # Python .gitignore (4500+ lines)
├── .gitattributes                   # Line ending config (if --git)
├── my_pipeline/                     # Main package (no src/ folder)
│   ├── __init__.py                  # Package exports
│   ├── _version.py                  # Auto-generated version (if --git)
│   ├── pipelines/                   # Pipeline orchestrators
│   │   └── __init__.py
│   ├── schemas/                     # Database schemas (user-created)
│   │   └── __init__.py
│   └── utils/                       # Framework utilities
│       ├── __init__.py
│       ├── columns.py               # ✏️ Column generation utilities
│       ├── databases.py             # ✏️ Database/schema constants
│       ├── tables.py                # ✏️ TableConfig definitions
│       ├── decorators.py            # ⚙️ Timing, checks, validation
│       ├── etl.py                   # ⚙️ Snowpark session singleton
│       ├── logger.py                # ⚙️ Structured logging
│       ├── table_cache.py           # ⚙️ Table pre-loading cache
│       ├── date_parser.py           # ⚙️ Date utilities
│       └── snowflake_utils.py       # ⚙️ Snowflake helpers
└── tests/                           # Integration tests
    └── basic_test.py                # Placeholder test
```

**Legend:**
- **✏️ USER EDITABLE** - Safe and encouraged to modify
- **⚙️ FRAMEWORK** - Auto-generated, do not modify (marked in file headers)

Git repository with initial commit is created if `--git` flag is used.

---

### `pypeline create-pipeline`

Creates a new pipeline within an existing pypeline project.

**Usage:**
```bash
pypeline create-pipeline --name customer-segmentation
```

**Options:**
- `--name TEXT` - Pipeline name (required)
  - Accepts alphanumeric, hyphens, underscores
  - Normalizes to lowercase with underscores
  - Generates PascalCase class name with "Pipeline" suffix

**What it creates:**
```
pipelines/{pipeline_name}/
├── {pipeline_name}_runner.py    # Main orchestrator
├── config.py                     # Pipeline-specific configuration
├── README.md                     # Documentation template
├── processors/                   # Processor classes
│   └── __init__.py
└── tests/                        # Integration tests
    └── __init__.py
```

**Features:**
- Auto-registers pipeline class in package `__init__.py`
- Enables top-level imports: `from my_project import CustomerSegmentationPipeline`
- Includes template methods for run(), pipeline(), run_processors(), and _write_to_snowflake()

---

### `pypeline create-processor`

Creates a new processor within an existing pipeline.

**Usage:**
```bash
pypeline create-processor --name sales-extractor --pipeline customer-segmentation
```

**Options:**
- `--name TEXT` - Processor name (required)
- `--pipeline TEXT` - Pipeline name where processor will be created (required)

**What it creates:**
```
pipelines/{pipeline}/processors/
├── {processor_name}_processor.py           # Processor class
└── tests/
    └── test_{processor_name}_processor.py  # Unit tests
```

**Features:**
- Auto-imports Logger, ETL, time_function decorator
- Scaffolds `__init__()` for extraction
- Scaffolds `process()` method for transformations
- Auto-registers import in pipeline runner file
- Includes pytest test template with fixtures

**Example generated processor:**
```python
class SalesExtractorProcessor:
    def __init__(self):
        self.logger = Logger()
        self.etl = ETL()
        # TODO: Extract data using TableConfig

    @time_function(f"{MODULE_NAME}.process")
    def process(self) -> DataFrame:
        # TODO: Implement transformations
        pass
```

---

### `pypeline sync-deps`

Synchronizes dependencies from `dependencies.py` to `pyproject.toml`.

**Usage:**
```bash
pypeline sync-deps
```

**Workflow:**
1. Edit `dependencies.py`:
   ```python
   DEFAULT_DEPENDENCIES = [
       "snowflake-snowpark-python>=1.42.0",
       "pandas>=2.2.0",
       "requests>=2.31.0",  # Added
   ]
   ```
2. Run `pypeline sync-deps`
3. `pyproject.toml` is automatically updated with proper formatting

**Why this approach?**
- User-friendly: Edit a simple Python list instead of TOML
- Version control friendly: Track changes in readable format
- Validation: Automatic validation of version specifiers
- No manual TOML editing errors

---

### `pypeline install`

Creates virtual environment and installs project dependencies.

**Usage:**
```bash
cd your-project
pypeline install
```

**What it does:**
1. Detects Python 3.12 or 3.13 on your system
2. Creates `.venv` directory
3. Upgrades pip to latest version
4. Installs project in editable mode
5. Installs all dependencies from `pyproject.toml`

**Requirements:**
- Python 3.12 or 3.13 must be available on system
- Project must have valid `pyproject.toml`

---

### `pypeline build`

Creates a Snowflake-compatible ZIP archive of your project with `pyproject.toml` at the root level.

**Usage:**
```bash
cd your-project
pypeline build
```

**What it does:**
1. Finds project root and reads `pyproject.toml` for project name and version
2. Cleans existing `dist/snowflake/` directory
3. Creates ZIP archive with all project files
4. Ensures `pyproject.toml` is at ZIP root level (critical for Snowflake)
5. Excludes build artifacts, venv, and cache files
6. Verifies structure and displays upload instructions

**Output:**
```
dist/
└── snowflake/
    └── my_project-0.1.0.zip    # Snowflake-ready ZIP
```

**ZIP Contents:**
When extracted, the ZIP contains your project files at the root level:
```
my_project-0.1.0.zip
├── pyproject.toml           # At root - required by Snowflake
├── my_project/              # Package at root - importable
│   ├── __init__.py
│   ├── pipelines/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
```

**Why This Structure Matters:**
Snowflake stages are strict about ZIP structure:
- ✅ Correct: `pyproject.toml` at root → Snowflake can import the package
- ❌ Wrong: `project_folder/pyproject.toml` → Snowflake import fails

pypeline build ensures the correct structure automatically.

**Excluded from ZIP:**
- `.venv/` - Virtual environment
- `dist/` - Distribution files
- `__pycache__/`, `.pytest_cache/` - Python caches
- `.git/` - Git repository
- `*.pyc`, `*.pyo`, `.DS_Store` - Build artifacts

**Requirements:**
- Must run from within a pypeline project (looks for `pyproject.toml` with `[tool.pypeline]`)
- Project must have valid `pyproject.toml`

**Best Practices:**
- Run `pypeline build` before deploying to Snowflake
- Version your project:
  - With git: `git tag v0.1.0` (if using `--git` flag during init)
  - Without git: Update `version` in `pyproject.toml` manually
- Review excluded files - ensure no sensitive data is included
- Test ZIP structure with `unzip -l dist/snowflake/*.zip`

---

## Project Structure

When you run `pypeline init --name my_pipeline`, it creates:

```
my_pipeline/
├── my_pipeline/                     # Package directory (no src/ folder)
│   ├── __init__.py              # Auto-generated imports
│   ├── _version.py              # Git tag-based versioning (if using --git)
│   ├── pipelines/               # Your pipeline implementations
│   │   └── __init__.py
│   ├── schemas/                 # Data schema definitions
│   │   └── __init__.py
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── databases.py         # ✏️ USER EDITABLE - Database constants
│       ├── tables.py            # ✏️ USER EDITABLE - Table configurations
│       ├── etl.py               # ⚙️ FRAMEWORK - Snowpark session manager
│       ├── logger.py            # ⚙️ FRAMEWORK - Structured logging
│       ├── decorators.py        # ⚙️ FRAMEWORK - Timing, table checks
│       ├── date_parser.py       # ⚙️ FRAMEWORK - DateTime utilities
│       ├── snowflake_utils.py   # ⚙️ FRAMEWORK - Snowflake helpers
│       └── columns.py           # ⚙️ FRAMEWORK - Column utilities
├── tests/                           # Integration tests
│   └── test_basic.py
├── dependencies.py                  # ✏️ USER EDITABLE - Dependency management
├── pyproject.toml                   # Project configuration
├── LICENSE                          # Your chosen license
├── README.md                        # Project readme
└── .gitignore                       # Python gitignore
```

### File Annotations

- **✏️ USER EDITABLE** - Safe and encouraged to modify
- **⚙️ FRAMEWORK** - Auto-generated, do not modify (marked in file headers)

---

## Example Generated Structures

### Complete Project Example

Here's what `pypeline init --name customer_analytics` creates:

```
customer_analytics/
├── pyproject.toml                      # Auto-generated project config
├── dependencies.py                     # ✏️ User-managed dependency list
├── LICENSE                             # Selected license (MIT, Apache, etc.)
├── README.md                           # Project documentation template
├── .gitignore                          # Python .gitignore (4500+ lines)
├── .gitattributes                      # Line ending config (if using --git)
├── customer_analytics/                 # Main package
│   ├── __init__.py                     # Auto-registered pipeline imports
│   ├── pipelines/                      # Pipeline implementations
│   │   └── __init__.py
│   ├── schemas/                        # Data schema definitions
│   │   └── __init__.py
│   └── utils/                          # Utility modules
│       ├── __init__.py
│       ├── columns.py                  # ✏️ Column generation utilities
│       ├── databases.py                # ✏️ Database/schema constants
│       ├── tables.py                   # ✏️ TableConfig definitions
│       ├── decorators.py               # ⚙️ Timing, checks, validation
│       ├── etl.py                      # ⚙️ Snowpark session singleton
│       ├── logger.py                   # ⚙️ Structured logging
│       ├── table_cache.py              # ⚙️ Table pre-loading cache
│       ├── date_parser.py              # ⚙️ Date utilities
│       └── snowflake_utils.py          # ⚙️ Snowflake helpers
└── tests/                              # Integration tests
    └── basic_test.py                   # Placeholder test
```

---

### Pipeline Structure Example

After running `pypeline create-pipeline --name customer-segmentation`:

```
customer_analytics/pipelines/customer_segmentation/
├── __init__.py
├── customer_segmentation_runner.py     # Main pipeline orchestrator
├── config.py                            # Pipeline-specific TableConfigs
├── README.md                            # Pipeline documentation
├── processors/                          # Processor implementations
│   └── __init__.py
└── tests/                               # Integration tests
    └── __init__.py
```

**Key Components:**

The generated `customer_segmentation_runner.py` includes:

- **`__init__()`** - Initializes Logger, ETL, and TableCache for pre-loading input tables
- **`run(_write: bool)`** - Entry point with `@time_function` decorator
- **`pipeline(_write: bool)`** - Orchestrates processors and conditional write logic
- **`run_processors()`** - Instantiates and chains processor transformations
- **`_write_to_snowflake()`** - Writes final DataFrame to Snowflake

The generated `config.py` provides:
- Import statements for `Database`, `Schema`, `TableConfig`, and `MonthlyColumnConfig`
- TODO comments with examples for defining TABLE_CONFIGS
- TODO comments with examples for monthly column configurations
- Structure for pipeline-specific constants

For complete implementation examples with TableCache usage, processor instantiation, and TableConfig definitions, see the [Quick Start Tutorial](#quick-start-tutorial) above.

**Generated `config.py`:**

```python
"""
CustomerSegmentationPipeline Pipeline Configuration

Pipeline-specific constants and configuration values.

This module imports from the project's utility modules (databases.py, tables.py, columns.py)
to help you define pipeline-specific table configurations and constants.
"""

from typing import Dict, Final

# Import project utilities - customize as needed
from ...utils.databases import Database, Schema
from ...utils.tables import TableConfig
from ...utils.columns import MonthlyColumnConfig

# TODO: Add pipeline-specific configuration
# Examples:
# - Table configurations using TableConfig
# - Source and destination table definitions
# - Date ranges and processing parameters
# - Feature flags

# Example table configurations using Dict[str, TableConfig]:
# TABLE_CONFIGS: Dict[str, TableConfig] = {
#     "source": TableConfig(
#         database=Database.PRODUCTION,
#         schema=Schema.RAW,
#         table_name_template="source_data_{YYYY}",
#         type="YEARLY",
#         is_output=False
#     ),
#     "destination": TableConfig(
#         database=Database.ANALYTICS,
#         schema=Schema.PROCESSED,
#         table_name_template="customer_segmentation_output",
#         type="STABLE"
#         is_output=True
#     )
# }

# Example monthly column configurations using Dict[str, MonthlyColumnConfig]:
# MONTHLY_COLUMNS: Dict[str, MonthlyColumnConfig] = {
#     "revenue": MonthlyColumnConfig(
#         prefix="rev_",
#         length=12,
#         format_type="currency",
#         label_template="{month} Revenue"
#     ),
#     "units": MonthlyColumnConfig(
#         prefix="units_",
#         length=12,
#         format_type="integer",
#         label_template="{month} Units Sold",
#         _output_prefix="unit_count_"
#     )
# }

# Example constants:
# PIPELINE_NAME: Final[str] = "customer_segmentation"
# PROCESSING_START_DATE: Final[str] = "2024-01-01"
```

---

### Processor Structure Example

After running `pypeline create-processor --name sales-enrichment --pipeline customer-segmentation`:

```
customer_analytics/pipelines/customer_segmentation/processors/
├── __init__.py
├── sales_enrichment_processor.py       # Processor implementation
└── tests/
    ├── __init__.py
    └── test_sales_enrichment_processor.py  # Unit tests
```

**Generated `sales_enrichment_processor.py`:**

```python
from pathlib import Path
from typing import Final

from snowflake.snowpark import DataFrame

from ....utils.etl import ETL
from ....utils.logger import Logger
from ....utils.decorators import time_function
from ....utils.table_cache import TableCache

MODULE_NAME: Final[str] = Path(__file__).name


class SalesEnrichmentProcessor:
    """
    Sales enrichment processor.

    TODO: Add processor description and transformation logic overview.
    """

    def __init__(self, cache: TableCache):
        """
        Initialize processor and extract data.

        Args:
            cache: Pre-populated TableCache from pipeline
        """
        self.logger = Logger()
        self.etl = ETL()
        self.cache = cache

        # TODO: Extract data using cache
        # self.sales_df = cache.get_table("sales")

        self.logger.info(
            message="Initialized SalesEnrichmentProcessor",
            context=MODULE_NAME
        )

    @time_function(f"{MODULE_NAME}.process")
    def process(self) -> DataFrame:
        """
        Transform data through orchestrated steps.

        TODO: Implement transformation logic

        Returns:
            Transformed DataFrame
        """
        self.logger.info(
            message="Processing sales enrichment transformations",
            context=MODULE_NAME
        )

        # TODO: Chain transformation methods
        # df = self._filter_valid_sales()
        # df = self._enrich_with_customer_data(df)
        # df = self._calculate_metrics(df)
        # return df

        pass

    # TODO: Add private transformation methods
    # def _filter_valid_sales(self) -> DataFrame:
    #     """Filter to valid sales records."""
    #     pass
```

**Generated `test_sales_enrichment_processor.py`:**

```python
import pytest
from unittest.mock import Mock, MagicMock
from snowflake.snowpark import DataFrame

from customer_analytics.pipelines.customer_segmentation.processors.sales_enrichment_processor import (
    SalesEnrichmentProcessor
)


@pytest.fixture
def mock_snowpark_session():
    """Mock Snowpark session."""
    return Mock()


@pytest.fixture
def mock_dataframe(mock_snowpark_session):
    """Mock Snowpark DataFrame."""
    df = MagicMock(spec=DataFrame)
    df.session = mock_snowpark_session
    return df


@pytest.fixture
def mock_cache(mock_dataframe):
    """Mock TableCache with pre-loaded tables."""
    cache = Mock()
    cache.get_table.return_value = mock_dataframe
    return cache


def test_sales_enrichment_processor_init(mock_cache):
    """Test SalesEnrichmentProcessor initialization."""
    processor = SalesEnrichmentProcessor(cache=mock_cache)

    assert processor is not None
    assert processor.logger is not None
    assert processor.etl is not None
    assert processor.cache == mock_cache


def test_sales_enrichment_processor_process(mock_cache, mock_dataframe):
    """Test SalesEnrichmentProcessor.process() method."""
    processor = SalesEnrichmentProcessor(cache=mock_cache)

    # TODO: Add test assertions for process() method
    # result = processor.process()
    # assert result is not None
    pass
```

---

### Import Auto-Registration Example

**Package `__init__.py` after creating pipelines:**

```python
# customer_analytics/__init__.py
# Auto-generated imports - DO NOT EDIT MANUALLY

from .pipelines.customer_segmentation.customer_segmentation_runner import CustomerSegmentationPipeline
from .pipelines.order_fulfillment.order_fulfillment_runner import OrderFulfillmentPipeline
from .pipelines.inventory_sync.inventory_sync_runner import InventorySyncPipeline

__all__ = [
    "CustomerSegmentationPipeline",
    "OrderFulfillmentPipeline",
    "InventorySyncPipeline",
]
```

**Pipeline runner after creating processors:**

```python
# customer_segmentation_runner.py
# Auto-registered processor imports

from .processors.sales_extractor_processor import SalesExtractorProcessor
from .processors.customer_enrichment_processor import CustomerEnrichmentProcessor
from .processors.segmentation_logic_processor import SegmentationLogicProcessor

class CustomerSegmentationPipeline:
    def __init__(self):
        self.logger = Logger()
        self.etl = ETL()
        self.cache = TableCache()

        # Auto-registered processor instances
        self.sales_extractor = SalesExtractorProcessor(self.cache)
        self.customer_enrichment = CustomerEnrichmentProcessor(self.cache)
        self.segmentation_logic = SegmentationLogicProcessor(self.cache)
```

---

### Dependencies Management Example

**`dependencies.py` structure:**

```python
"""
Project dependencies management.

Edit the USER_DEPENDENCIES list below, then run:
    pypeline sync-deps

DO NOT EDIT the BASE_DEPENDENCIES section - it's auto-generated.
"""

# ============================================================================
# BASE DEPENDENCIES (Auto-generated - DO NOT MODIFY)
# ============================================================================
BASE_DEPENDENCIES = [
    "snowflake-snowpark-python>=1.42.0",
    "numpy>=1.26.0",
    "pandas>=2.2.0",
    "build>=1.2.2",
    "pytest>=8.3.0",
    "ruff>=0.11.0",
]

# ============================================================================
# USER DEPENDENCIES (Edit this section)
# ============================================================================
USER_DEPENDENCIES = [
    "requests>=2.31.0",
    "pydantic>=2.5.0",
    "python-dateutil>=2.8.2",
]

# Final merged list
DEFAULT_DEPENDENCIES = BASE_DEPENDENCIES + USER_DEPENDENCIES
```

**After running `pypeline sync-deps`, `pyproject.toml` is updated:**

```toml
[project]
dependencies = [
    "snowflake-snowpark-python>=1.42.0",
    "numpy>=1.26.0",
    "pandas>=2.2.0",
    "build>=1.2.2",
    "pytest>=8.3.0",
    "ruff>=0.11.0",
    "requests>=2.31.0",
    "pydantic>=2.5.0",
    "python-dateutil>=2.8.2",
]
```

---

### Build Output Example

After running `pypeline build`:

```
dist/
└── snowflake/
    └── customer_analytics-0.1.0.zip
```

**ZIP structure (verified by pypeline build):**

```
customer_analytics-0.1.0.zip
├── pyproject.toml                      # ✅ At root - required by Snowflake
├── customer_analytics/                 # ✅ Package at root - importable
│   ├── __init__.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── customer_segmentation/
│   │       ├── __init__.py
│   │       ├── customer_segmentation_runner.py
│   │       ├── config.py
│   │       └── processors/
│   │           ├── __init__.py
│   │           └── sales_enrichment_processor.py
│   └── utils/
│       ├── __init__.py
│       ├── etl.py
│       ├── logger.py
│       ├── tables.py
│       ├── databases.py
│       └── table_cache.py
```

**Snowflake deployment:**

```sql
-- Upload ZIP to Snowflake stage
PUT file://dist/snowflake/customer_analytics-0.1.0.zip
  @my_stage
  AUTO_COMPRESS=FALSE;

-- Create procedure using the pipeline
CREATE OR REPLACE PROCEDURE run_customer_segmentation()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.12'
PACKAGES = ('snowflake-snowpark-python')
IMPORTS = ('@my_stage/customer_analytics-0.1.0.zip')
HANDLER = 'customer_analytics.pipelines.customer_segmentation.customer_segmentation_runner.CustomerSegmentationPipeline.run';

-- Execute pipeline in Snowflake
CALL run_customer_segmentation();
```

---

## Development Workflow

### Recommended Development Process

```
1. Initialize Project
   ↓
2. Configure Databases & Tables
   ↓
3. Create Pipeline(s)
   ↓
4. Create Processors
   ↓
5. Implement Extraction Logic (in processor __init__)
   ↓
6. Implement Transformation Logic (in processor.process())
   ↓
7. Wire Processors in Pipeline Runner
   ↓
8. Write Tests
   ↓
9. Run & Iterate
```

### Typical Development Session

```bash
# 1. Create a new pipeline
pypeline create-pipeline --name order-fulfillment

# 2. Add processors for each data source or transformation
pypeline create-processor --name orders-extractor --pipeline order-fulfillment
pypeline create-processor --name inventory-check --pipeline order-fulfillment
pypeline create-processor --name fulfillment-logic --pipeline order-fulfillment

# 3. Configure table configs in pipeline's config.py
# Edit: my_project/pipelines/order_fulfillment/config.py

# 4. Implement each processor
# Edit: processors/orders_extractor_processor.py
# Edit: processors/inventory_check_processor.py
# Edit: processors/fulfillment_logic_processor.py

# 5. Wire processors in runner
# Edit: order_fulfillment_runner.py

# 6. Add dependencies if needed
# Edit: dependencies.py
pypeline sync-deps
pypeline install

# 7. Run pipeline
python -m my_project.pipelines.order_fulfillment.order_fulfillment_runner

# 8. Write tests
# Edit: processors/tests/test_orders_extractor_processor.py
pytest tests/

# 9. Build Snowflake distribution
pypeline build

# 10. Deploy to Snowflake
# Upload dist/snowflake/*.zip to Snowflake stage
```

### Adding New Dependencies

```bash
# 1. Edit dependencies.py
echo 'DEFAULT_DEPENDENCIES = ["snowflake-snowpark-python>=1.42.0", "pandas>=2.2.0", "numpy>=1.26.0"]' > dependencies.py

# 2. Sync to pyproject.toml
pypeline sync-deps

# 3. Install
pypeline install
```

### Versioning and Releases

pypeline projects use hatch-vcs for automatic versioning from git tags:

```bash
# Make changes and commit
git add .
git commit -m "Add order fulfillment pipeline"

# Create version tag
git tag -a v0.1.0 -m "Initial release"

# Push with tags
git push origin main --tags

# Version is automatically set to 0.1.0
```

---

## ETL Architecture & Best Practices

### The Processor Pattern

pypeline-cli follows a **Processor Pattern** with centralized extraction for organizing ETL logic:

```
Pipeline.__init__()
    ↓
Extract: Pre-load input tables into TableCache
    ↓
Pipeline.run_processors()
    ↓
Processor 1(cache) → Transform
    ↓
Processor 2(cache) → Transform
    ↓
Processor 3(cache) → Transform
    ↓
Pipeline._write_to_snowflake() → Load
```

**Key Principles:**

1. **Extraction happens at Pipeline level**
   - Pipeline's `__init__()` pre-loads all input tables into TableCache
   - TableCache uses TableConfig from `config.py` for dynamic table names
   - Each table loaded **once**, eliminating redundant Snowflake queries
   - Cache is shared across all processors

2. **Transformation happens in Processor `process()`**
   - Processors receive pre-populated cache in `__init__(cache)`
   - Access cached tables via `self.cache.get_table("table_key")`
   - `process()` method orchestrates transformations
   - Private methods implement atomized transformation steps
   - Returns final DataFrame

3. **Loading happens in Pipeline Runner**
   - Pipeline orchestrates all processors with shared cache
   - Pipeline handles final write to Snowflake via `_write_to_snowflake()`
   - Conditional writes based on `_write` flag

### Extract, Transform, Load (ETL) Stages

#### **Stage 1: Extract**

**Where:** Pipeline `__init__()` method using TableCache

**Purpose:** Pre-load all input tables once and share across processors

**Best Practices:**
- Define all TableConfigs in `config.py`
- Pre-load tables in pipeline `__init__()` using `TableCache.preload_tables()`
- Mark output tables with `is_output=True` to exclude from pre-loading
- Log cache statistics for monitoring
- Pass cache to all processors

**Example:**

```python
from ...utils.table_cache import TableCache
from .config import TABLE_CONFIGS

class OrderFulfillmentPipeline:
    def __init__(self, year: int, month: int):
        self.logger = Logger()
        self.etl = ETL()
        self.year = year
        self.month = month

        # Extract: Pre-load all input tables into cache (one-time operation)
        self.cache = TableCache().preload_tables(
            table_keys=[k for k, config in TABLE_CONFIGS.items() if not config.is_output],
            table_configs=TABLE_CONFIGS
        )

        self.logger.info(
            message=f"Pre-loaded {len(self.cache.tables)} input tables into cache",
            context="OrderFulfillmentPipeline.__init__"
        )

    def run_processors(self):
        # All processors receive the same pre-populated cache
        orders_proc = OrdersProcessor(self.cache)
        inventory_proc = InventoryProcessor(self.cache)

        df = orders_proc.process()
        df = inventory_proc.process(df)
        return df
```

**config.py:**

```python
from ..utils.tables import TableConfig
from ..utils.databases import Database, Schema

TABLE_CONFIGS = {
    "orders": TableConfig(
        database=Database.RAW,
        schema=Schema.LANDING,
        table_name_template="orders_{MM}",
        type="MONTHLY",
        month=3,
        is_output=False  # Input table - will be pre-loaded
    ),
    "customers": TableConfig(
        database=Database.PROD,
        schema=Schema.DIM,
        table_name_template="dim_customers",
        type="STABLE",
        is_output=False  # Input table - will be pre-loaded
    ),
    "output": TableConfig(
        database=Database.PROD,
        schema=Schema.ANALYTICS,
        table_name_template="order_summary",
        type="STABLE",
        is_output=True  # Output table - NOT pre-loaded
    ),
}
```

**Architecture Diagram:**

```
┌────────────────────────────────────────────┐
│  Pipeline.__init__()                       │
├────────────────────────────────────────────┤
│ 1. Initialize Logger, ETL                  │
│ 2. Initialize TableCache                   │
│ 3. Call preload_tables() with configs      │
│    - Reads TABLE_CONFIGS from config.py    │
│    - Generates table names dynamically     │
│    - Loads each input table from Snowflake │
│    - Stores in cache.tables dict           │
│ 4. Log cache statistics                    │
└────────────────────────────────────────────┘
         │
         ▼
   self.cache.tables = {
       "orders": DataFrame,
       "customers": DataFrame
   }
         │
         ▼
   Pass to all processors
```

#### **Stage 2: Transform**

**Where:** Processor `process()` method and private methods

**Purpose:** Clean, filter, join, aggregate, and enrich data

**Best Practices:**
- Break transformations into small, focused private methods
- Each method should do ONE thing well
- Use descriptive method names (`_filter_active_customers`, not `_step1`)
- Chain transformations for readability
- Add comments explaining business logic

**Example:**

```python
from ....utils.decorators import time_function
from ....utils.logger import Logger

class OrdersTransformProcessor:
    def __init__(self, cache):
        """
        Receive pre-populated cache from pipeline.

        Args:
            cache: TableCache with pre-loaded input tables
        """
        self.logger = Logger()
        self.cache = cache

        # Access pre-loaded tables from cache (no Snowflake query)
        self.orders_df = cache.get_table("orders")
        self.customers_df = cache.get_table("customers")

    @time_function(f"{MODULE_NAME}.process")
    def process(self) -> DataFrame:
        """
        Transform orders data: filter, enrich, aggregate.

        Business Logic:
        1. Filter to completed orders only
        2. Calculate order totals
        3. Add customer tier from lookup
        4. Aggregate to daily summaries

        Returns:
            Transformed DataFrame ready for segmentation
        """
        self.logger.info(
            message="Starting orders transformation",
            context=MODULE_NAME
        )

        # Chain transformations
        df = self._filter_completed_orders()
        df = self._calculate_order_totals(df)
        df = self._enrich_customer_tier(df)
        df = self._aggregate_daily_summary(df)

        return df

    def _filter_completed_orders(self) -> DataFrame:
        """
        Filter to completed orders with valid amounts.

        Business Rule: Only include orders with STATUS='COMPLETED'
        and TOTAL_AMOUNT > 0
        """
        return self.orders_df.filter(
            (col("STATUS") == "COMPLETED") &
            (col("TOTAL_AMOUNT") > 0)
        )

    def _calculate_order_totals(self, df: DataFrame) -> DataFrame:
        """
        Calculate final order total including tax and shipping.

        Formula: SUBTOTAL + TAX + SHIPPING - DISCOUNT
        """
        return df.with_column(
            "FINAL_TOTAL",
            col("SUBTOTAL") + col("TAX") + col("SHIPPING") - col("DISCOUNT")
        )

    def _enrich_customer_tier(self, df: DataFrame) -> DataFrame:
        """
        Join customer tier from pre-loaded customers table.

        Adds CUSTOMER_TIER column based on lifetime value.
        """
        # Use pre-loaded customer data from cache (no additional query)
        return df.join(
            self.customers_df.select("CUSTOMER_ID", "CUSTOMER_TIER"),
            on="CUSTOMER_ID",
            how="left"
        )

    def _aggregate_daily_summary(self, df: DataFrame) -> DataFrame:
        """
        Aggregate orders to daily summary by customer tier.

        Returns:
            DataFrame with ORDER_DATE, CUSTOMER_TIER, TOTAL_ORDERS, TOTAL_REVENUE
        """
        return df.group_by("ORDER_DATE", "CUSTOMER_TIER").agg(
            count("ORDER_ID").alias("TOTAL_ORDERS"),
            sum_("FINAL_TOTAL").alias("TOTAL_REVENUE")
        )
```

**Architecture Diagram:**

```
┌────────────────────────────────────────┐
│  Processor.__init__(cache)             │
├────────────────────────────────────────┤
│  1. Store cache reference              │
│  2. Access pre-loaded tables:          │
│     - orders_df = cache.get_table()    │
│     - customers_df = cache.get_table() │
└────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│  Processor.process()                   │
├────────────────────────────────────────┤
│  1. _filter_completed_orders()         │
│       │                                 │
│       ▼                                 │
│  2. _calculate_order_totals(df)        │
│       │                                 │
│       ▼                                 │
│  3. _enrich_customer_tier(df)          │
│       │  (uses cached customers_df)    │
│       ▼                                 │
│  4. _aggregate_daily_summary(df)       │
│       │                                 │
│       ▼                                 │
│  return final_df                       │
└────────────────────────────────────────┘
```

**Transformation Best Practices:**

| ✅ Do | ❌ Don't |
|------|---------|
| Use descriptive method names | Use generic names like `_transform1()` |
| One transformation per method | Combine unrelated transformations |
| Document business logic in docstrings | Write code without context |
| Chain method calls for clarity | Create deeply nested transformations |
| Use Snowpark operations | Pull large data to pandas unnecessarily |
| Log transformation steps | Transform silently without metrics |

#### **Stage 3: Load**

**Where:** Pipeline Runner `_write_to_snowflake()` method

**Purpose:** Write final DataFrame to Snowflake table

**Best Practices:**
- Centralize write logic in pipeline runner (not processors)
- Use conditional writes with `_write` flag
- Log table paths and write modes
- Consider write modes carefully (overwrite vs append vs truncate)

**Example:**

```python
class OrderFulfillmentPipeline:
    def __init__(self, year: int, month: int):
        self.logger = Logger()
        self.etl = ETL()
        self.year = year
        self.month = month

    @time_function("OrderFulfillmentPipeline.run")
    def run(self, _write: bool = False):
        """
        Entry point for pipeline execution.

        Args:
            _write: If True, writes results to Snowflake. If False, runs
                    transformations but doesn't write (useful for testing).
        """
        self.pipeline(_write)
        self.logger.info(
            message="Order fulfillment pipeline completed successfully",
            context=MODULE_NAME
        )

    def pipeline(self, _write: bool):
        """
        Orchestrate processors and conditional write.

        Args:
            _write: If True, writes to Snowflake
        """
        # Run processors
        df: DataFrame = self.run_processors()

        # Conditional write
        if _write:
            # Generate target table name
            table_path = f"PRODUCTION.ANALYTICS.order_summary_{self.year}_{self.month:02d}"

            # Write to Snowflake
            self._write_to_snowflake(
                df=df,
                write_mode="overwrite",  # Replace existing data
                table_path=table_path
            )
        else:
            self.logger.info(
                message="Skipping write (_write=False). Transformation complete.",
                context=MODULE_NAME
            )

    def run_processors(self) -> DataFrame:
        """
        Instantiate and run processors in sequence.

        Returns:
            Final transformed DataFrame
        """
        # Extract and transform orders
        orders_processor = OrdersExtractorProcessor(year=self.year, month=self.month)
        orders_df = orders_processor.process()

        # Check inventory
        inventory_processor = InventoryCheckProcessor(orders_df=orders_df)
        checked_df = inventory_processor.process()

        # Apply fulfillment logic
        fulfillment_processor = FulfillmentLogicProcessor(checked_df=checked_df)
        final_df = fulfillment_processor.process()

        return final_df

    def _write_to_snowflake(
        self,
        df: DataFrame,
        write_mode: Literal["append", "overwrite", "truncate"],
        table_path: str,
    ):
        """
        Write DataFrame to Snowflake table.

        Args:
            df: DataFrame to write
            write_mode: Write mode for save_as_table
                - "overwrite": Drop and recreate table
                - "append": Add rows to existing table
                - "truncate": Delete all rows, keep schema
            table_path: Fully qualified table name (DATABASE.SCHEMA.TABLE)
        """
        self.logger.info(
            message=f"Writing DataFrame to {table_path} (mode={write_mode})",
            context=MODULE_NAME
        )

        # Write to Snowflake
        df.write.mode(write_mode).save_as_table(table_path)

        # Log success metrics
        row_count = df.count()
        self.logger.info(
            message=f"Successfully wrote {row_count} rows to {table_path}",
            context=MODULE_NAME
        )
```

**Architecture Diagram:**

```
┌───────────────────────────────────────────┐
│  Pipeline.run(_write=True)                │
├───────────────────────────────────────────┤
│  1. Call pipeline(_write)                 │
│       │                                    │
│       ▼                                    │
│  2. Run processors (Extract + Transform)  │
│       │                                    │
│       ▼                                    │
│  3. Check _write flag                     │
│       │                                    │
│       ├─ If True:                          │
│       │    ├─ Generate table path         │
│       │    ├─ Call _write_to_snowflake()  │
│       │    └─ Log success                 │
│       │                                    │
│       └─ If False:                         │
│            └─ Log skip                     │
└───────────────────────────────────────────┘
```

**Write Modes Comparison:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `overwrite` | Drop and recreate table | Full refresh, schema changes |
| `append` | Add rows to existing table | Incremental loads, partitioned data |
| `truncate` | Delete rows, keep schema | Full refresh with stable schema |
| `errorifexists` | Fail if table exists | First-time table creation |
| `ignore` | Skip if table exists | Idempotent operations |

### Complete ETL Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│               PIPELINE ORCHESTRATOR                             │
│                                                                 │
│  __init__():                                                    │
│    ├─ Initialize Logger, ETL                                    │
│    └─ EXTRACT: Pre-load tables into TableCache                 │
│         - Read TABLE_CONFIGS from config.py                    │
│         - Load each input table (is_output=False)              │
│         - Store in self.cache.tables dict                      │
│                                                                 │
│  run(_write: bool):                                             │
│    └─ Call pipeline(_write)                                    │
│                                                                 │
│  pipeline(_write):                                              │
│    ├─ Call run_processors()                                    │
│    └─ Conditionally write results                              │
│                                                                 │
│  run_processors():                                              │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼ (pass self.cache to each processor)
┌─────────────────────────────────────────────────────────────────┐
│                PROCESSOR 1: TRANSFORM                           │
│                                                                 │
│  __init__(cache):                                               │
│    - Store cache reference                                      │
│    - Access pre-loaded tables:                                  │
│      • self.orders_df = cache.get_table("orders")              │
│      • self.customers_df = cache.get_table("customers")        │
│                                                                 │
│  process():                                                     │
│    - _filter_valid_rows()                                       │
│    - _join_with_customers() [uses cached customers_df]         │
│    - _calculate_metrics()                                       │
│    - return df                                                  │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼ (pass cache and/or df)
┌─────────────────────────────────────────────────────────────────┐
│                PROCESSOR 2: TRANSFORM                           │
│                                                                 │
│  __init__(cache):                                               │
│    - Store cache reference                                      │
│    - Access any additional cached tables if needed              │
│                                                                 │
│  process(df):                                                   │
│    - _enrich_with_lookup() [may use cache.get_table()]         │
│    - _apply_business_rules()                                    │
│    - return df                                                  │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼ (pass cache and/or df)
┌─────────────────────────────────────────────────────────────────┐
│                PROCESSOR 3: TRANSFORM                           │
│                                                                 │
│  __init__(cache):                                               │
│    - Store cache reference                                      │
│                                                                 │
│  process(df):                                                   │
│    - _group_by_dimensions()                                     │
│    - _calculate_aggregates()                                    │
│    - return final_df                                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼ (return final_df to pipeline)
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE: LOAD                               │
│                                                                 │
│  if _write:                                                     │
│    _write_to_snowflake(df, "overwrite", "DB.SCHEMA.TABLE")    │
│      │                                                           │
│      ▼                                                           │
│    df.write.mode("overwrite").save_as_table("DB.SCHEMA.TABLE") │
│    Log success                                                  │
│  else:                                                          │
│    Log dry-run completion                                       │
│                                                                 │
│  Log pipeline completion                                        │
└─────────────────────────────────────────────────────────────────┘

Key: Extract happens ONCE at pipeline.__init__() via TableCache
     All processors receive shared cache and focus on Transform only
     Load happens at pipeline level via _write_to_snowflake()
```

---

## Built-in Utilities

pypeline-cli provides a comprehensive set of utility modules out-of-the-box. These are auto-generated in `{project}/utils/` during project initialization. Utilities fall into two categories:

- **⚙️ Framework Files** - Auto-generated, optimized utilities (marked "DO NOT MODIFY")
- **✏️ User-Editable Files** - Configuration files meant to be customized for your project

---

### ETL Singleton

**File:** `utils/etl.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Manages a single Snowpark session throughout your pipeline execution.

**Usage:**

```python
from ...utils.etl import ETL

etl = ETL()  # Get singleton instance
df = etl.session.table("DATABASE.SCHEMA.TABLE")

# Calling ETL() again returns the same instance
etl2 = ETL()
assert etl is etl2  # True
```

**Key Features:**
- **Singleton pattern** - Only one session per process
- **Lazy initialization** - Session created on first access
- **Thread-safe** - Single instance shared across pipeline
- **No manual connection management** - Uses `get_active_session()`

**Best Practices:**
- Instantiate in processor `__init__()`: `self.etl = ETL()`
- Access session via `self.etl.session`
- Don't create multiple ETL instances (they'll be the same object anyway)

---

### Logger

**File:** `utils/logger.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Provides structured, color-coded logging with context.

**Usage:**

```python
from ...utils.logger import Logger

logger = Logger()

logger.info(message="Pipeline started", context="CustomerPipeline")
logger.warning(message="Missing data for customer_id=123", context="OrdersProcessor")
logger.error(message="Failed to write table", context="Pipeline.load", customer_id=123)
logger.debug(message="Debug info", context="Dev")
logger.critical(message="Critical failure", context="System")
```

**Output Format:**
```
2025-03-15 14:30:22 | INFO | CustomerPipeline | Pipeline started
2025-03-15 14:30:25 | WARN | OrdersProcessor | Missing data for customer_id=123
2025-03-15 14:30:28 | ERROR | Pipeline.load | Failed to write table | customer_id=123
```

**Features:**
- Color-coded log levels (green=INFO, yellow=WARN, red=ERROR, etc.)
- Structured format: timestamp | level | context | message
- Support for key-value pairs (kwargs)
- Works in Snowflake and Databricks environments

**Best Practices:**
- Instantiate in `__init__()`: `self.logger = Logger()`
- Always provide `context` parameter (e.g., MODULE_NAME)
- Use appropriate levels (INFO for normal flow, ERROR for exceptions)
- Add kwargs for debugging: `logger.info(message="Processed", context=MODULE_NAME, row_count=1000)`

---

### TableConfig

**File:** `utils/tables.py` (✏️ User Editable)

**Purpose:** Manages dynamic table names with time-based partitioning.

**Table Types:**
1. **YEARLY** - Tables partitioned by year (e.g., `sales_2025`)
2. **MONTHLY** - Tables partitioned by month (e.g., `orders_03`)
3. **STABLE** - Static tables with no date suffix (e.g., `dim_customers`)

**Usage:**

```python
from ...utils.tables import TableConfig
from ...utils.databases import Database, Schema

# Define yearly sales table
SALES_TABLE = TableConfig(
    database=Database.ANALYTICS,
    schema=Schema.RAW,
    table_name_template="sales_{YYYY}",
    type="YEARLY"
)

# Generate table name for 2025
table_name = SALES_TABLE.generate_table_name(year=2025)
# Result: "ANALYTICS.RAW.sales_2025"

# Define monthly orders table
ORDERS_TABLE = TableConfig(
    database=Database.PRODUCTION,
    schema=Schema.PROCESSED,
    table_name_template="orders_{MM}",
    type="MONTHLY",
    month=3  # March
)

# Generate table name
table_name = ORDERS_TABLE.generate_table_name()
# Result: "PRODUCTION.PROCESSED.orders_03"

# Define stable dimension table
CUSTOMER_DIM = TableConfig(
    database=Database.ANALYTICS,
    schema=Schema.REPORTING,
    table_name_template="dim_customers",
    type="STABLE"
)

table_name = CUSTOMER_DIM.generate_table_name()
# Result: "ANALYTICS.REPORTING.dim_customers"
```

**Template Placeholders:**
- `{YYYY}` - 4-digit year (e.g., 2025)
- `{YY}` - 2-digit year (e.g., 25)
- `{MM}` - 2-digit month with leading zero (e.g., 01, 12)

**Best Practices:**
- Define all TableConfig instances in `utils/tables.py` or pipeline `config.py`
- Use constants for database and schema names from `utils/databases.py`
- Update month dynamically: `ORDERS_TABLE.month = 6` before calling `generate_table_name()`
- Pass year as parameter for yearly tables: `generate_table_name(year=2025)`

---

### Decorators

**File:** `utils/decorators.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Provides reusable decorators for timing, table checks, and freshness validation.

#### `@time_function`

Measures and logs function execution time.

**Usage:**

```python
from ...utils.decorators import time_function

@time_function("OrdersProcessor.process")
def process(self) -> DataFrame:
    # ... transformation logic ...
    return df

# Logs: "OrdersProcessor.process completed in 3.45 seconds."
```

**Best Practices:**
- Use on all `process()` methods
- Use on `run()` methods in pipelines
- Provide descriptive module names

#### `@skip_if_exists`

Skips function execution if table already exists.

**Usage:**

```python
from ...utils.decorators import skip_if_exists
from ...utils.etl import ETL

etl = ETL()

@skip_if_exists('ANALYTICS.STAGING.users_2024', etl)
def create_users_table():
    # Table creation logic
    pass

create_users_table()
# Logs: "Table ANALYTICS.STAGING.users_2024 already exists. Skipping create_users_table."
```

**Best Practices:**
- Use for idempotent table creation
- Provide full table path: `'DATABASE.SCHEMA.TABLE'`

#### `@skip_if_updated_this_month`

Skips function if table was updated this month (freshness check).

**Usage:**

```python
from ...utils.decorators import skip_if_updated_this_month
from ...utils.etl import ETL

etl = ETL()

@skip_if_updated_this_month('ANALYTICS.REPORTS.monthly_summary', etl)
def refresh_monthly_summary():
    # Refresh logic
    pass

refresh_monthly_summary()  # Skips if already updated this month
refresh_monthly_summary(override=True)  # Forces execution
```

**Best Practices:**
- Use for monthly refresh jobs
- Provides `override` parameter for manual runs
- Checks Snowflake's `SYSTEM$LAST_CHANGE_COMMIT_TIME`

---

### Databases

**File:** `utils/databases.py` (✏️ User Editable)

**Purpose:** Centralize database and schema constants.

**Usage:**

```python
# Define your constants
class Database:
    RAW = "RAW_DATA"
    STAGING = "STAGING"
    PROD = "PRODUCTION"
    ANALYTICS = "ANALYTICS_DB"

class Schema:
    LANDING = "LANDING_ZONE"
    TRANSFORM = "TRANSFORMED"
    ANALYTICS = "ANALYTICS"
    REPORTING = "REPORTING"

# Use throughout your project
from ...utils.databases import Database, Schema

table_name = f"{Database.PROD}.{Schema.ANALYTICS}.customer_segments"
# "PRODUCTION.ANALYTICS.customer_segments"
```

**Best Practices:**
- Define all database and schema names here
- Use class constants instead of string literals
- Reference in TableConfig definitions

---

### TableCache

**File:** `utils/table_cache.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Pre-loads and caches input tables to eliminate redundant Snowflake queries across processors.

**The Problem It Solves:**

Without TableCache, if multiple processors need the same input table, each processor would query Snowflake separately:

```python
# ❌ Without TableCache - Multiple redundant queries
class Processor1:
    def __init__(self):
        self.customer_df = etl.session.table("DB.SCHEMA.customers")  # Query 1

class Processor2:
    def __init__(self):
        self.customer_df = etl.session.table("DB.SCHEMA.customers")  # Query 2 (redundant!)
```

**With TableCache:**

```python
# ✅ With TableCache - Single query, shared across processors
class Pipeline:
    def __init__(self):
        self.cache = TableCache()
        # Pre-load all input tables once
        self.cache.add_table("customers", "DB.SCHEMA.customers")
        self.cache.add_table("orders", "DB.SCHEMA.orders")

    def run_processors(self):
        # All processors receive same cache instance
        processor1 = Processor1(self.cache)  # Uses cached customer_df
        processor2 = Processor2(self.cache)  # Reuses same customer_df
```

**Complete Example:**

```python
from ...utils.table_cache import TableCache
from ...utils.etl import ETL

class CustomerSegmentationPipeline:
    def __init__(self, month: int):
        self.logger = Logger()
        self.etl = ETL()
        self.month = month

        # Initialize cache
        self.cache = TableCache()

        # Pre-load all input tables
        self.cache.add_table("customers", "PROD.DIM.customers")
        self.cache.add_table("orders", f"PROD.FACT.orders_{month:02d}")
        self.cache.add_table("products", "PROD.DIM.products")

        self.logger.info(
            message=f"Pre-loaded {len(self.cache.tables)} tables into cache",
            context="CustomerSegmentationPipeline"
        )

    def run_processors(self):
        # Processors access pre-loaded tables from cache
        sales = SalesProcessor(self.cache)
        enrichment = EnrichmentProcessor(self.cache)
        segmentation = SegmentationProcessor(self.cache)

        df = sales.process()
        df = enrichment.process(df)
        df = segmentation.process(df)
        return df


class SalesProcessor:
    def __init__(self, cache: TableCache):
        self.cache = cache
        # Access pre-loaded table (no Snowflake query)
        self.orders_df = cache.get_table("orders")
        self.products_df = cache.get_table("products")

    def process(self) -> DataFrame:
        # Join using cached tables
        return self.orders_df.join(
            self.products_df,
            on="PRODUCT_ID",
            how="left"
        )
```

**Key Methods:**

- `add_table(name: str, table_path: str)` - Load and cache a table
- `get_table(name: str) -> DataFrame` - Retrieve cached table
- `tables` property - Dict of all cached tables

**Benefits:**
- **Performance**: Each table queried only once per pipeline run
- **Cost**: Reduces Snowflake compute credits
- **Simplicity**: Processors don't manage their own table loading
- **Consistency**: All processors work with identical data snapshots

**Best Practices:**
- Pre-load all input tables in pipeline `__init__()`
- Pass cache instance to all processors
- Use descriptive cache keys (e.g., "customers", "orders", "products")
- Log cache statistics for monitoring

---

### Columns Utilities

**File:** `utils/columns.py` (✏️ User Editable)

**Purpose:** Generate dynamic column names and manage column configurations for time-partitioned data.

**MonthlyColumnConfig:**

Useful for generating month-specific column names in wide-format tables.

**Example:**

```python
from ...utils.columns import MonthlyColumnConfig

# Define column configuration
REVENUE_COLUMNS = MonthlyColumnConfig(
    prefix="REVENUE",
    suffix="USD",
    separator="_"
)

# Generate column name for January
jan_col = REVENUE_COLUMNS.generate_column_name(month=1)
# Result: "REVENUE_01_USD"

# Generate column name for December
dec_col = REVENUE_COLUMNS.generate_column_name(month=12)
# Result: "REVENUE_12_USD"

# Use in DataFrame operations
df = df.with_column(
    REVENUE_COLUMNS.generate_column_name(month=3),
    col("MARCH_SALES") * col("PRICE")
)
```

**Use Cases:**
- Wide-format tables with monthly columns
- Pivot tables with time-based dimensions
- Budgeting and forecasting tables
- Year-over-year comparison tables

---

### Date Parser

**File:** `utils/date_parser.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Provides utilities for parsing, formatting, and manipulating dates in Snowflake pipelines.

**Common Functions:**

```python
from ...utils.date_parser import (
    parse_date,
    get_month_start,
    get_month_end,
    format_table_date
)

# Parse various date formats
date = parse_date("2025-03-15")
date = parse_date("03/15/2025")

# Get month boundaries
month_start = get_month_start(year=2025, month=3)  # 2025-03-01
month_end = get_month_end(year=2025, month=3)      # 2025-03-31

# Format dates for table names
table_suffix = format_table_date(year=2025, month=3)  # "2025_03"
```

**Best Practices:**
- Use for consistent date handling across pipelines
- Standardize date formats for table naming
- Handle month boundaries in time-partitioned data

---

### Snowflake Utilities

**File:** `utils/snowflake_utils.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Provides Snowflake-specific helper functions for common operations.

**Common Operations:**

```python
from ...utils.snowflake_utils import (
    table_exists,
    get_table_schema,
    execute_sql,
    grant_privileges
)

# Check if table exists
if table_exists("PROD.ANALYTICS.customer_segments"):
    logger.info("Table found")

# Get table schema
schema = get_table_schema("PROD.DIM.customers")

# Execute arbitrary SQL
execute_sql("GRANT SELECT ON TABLE customers TO ROLE analyst")

# Grant privileges
grant_privileges(
    table="PROD.ANALYTICS.revenue_summary",
    role="REPORTING_ROLE",
    privileges=["SELECT"]
)
```

**Use Cases:**
- Table existence checks before operations
- Schema validation and comparison
- Access control management
- Administrative operations

---

### Framework Files Summary

| Utility | File | Purpose | Modifiable |
|---------|------|---------|------------|
| **ETL Singleton** | `etl.py` | Snowpark session management | ⚙️ No |
| **Logger** | `logger.py` | Structured, color-coded logging | ⚙️ No |
| **Decorators** | `decorators.py` | Timing, table checks, freshness validation | ⚙️ No |
| **TableCache** | `table_cache.py` | Pre-load and cache input tables | ⚙️ No |
| **Date Parser** | `date_parser.py` | Date parsing and formatting utilities | ⚙️ No |
| **Snowflake Utils** | `snowflake_utils.py` | Snowflake-specific helper functions | ⚙️ No |
| **TableConfig** | `tables.py` | Dynamic table naming with time partitioning | ✏️ Yes |
| **Databases** | `databases.py` | Database and schema constants | ✏️ Yes |
| **Columns** | `columns.py` | Column generation utilities | ✏️ Yes |

**Key Principle:**

Framework files (⚙️) are optimized, tested utilities that handle infrastructure concerns. User-editable files (✏️) are meant for you to customize with your project-specific configurations. This separation ensures framework stability while providing flexibility for your business logic.

---

## Requirements

- **Python 3.12 or 3.13** (required)
  - Note: Python 3.14+ is not yet supported by snowflake-snowpark-python
- **Git** (for version management)
- **pipx** (recommended for installation)

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Setup:**

```bash
git clone https://github.com/dbrown540/pypeline-cli.git
cd pypeline-cli
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/dbrown540/pypeline-cli/issues)
- **PyPI:** [pypeline-cli on PyPI](https://pypi.org/project/pypeline-cli/)
- **Documentation:** This README

---

**Built with ❤️ for data engineers working with Snowflake and Snowpark.**
