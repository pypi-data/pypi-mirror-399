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

pypeline-cli is built on several core principles:

### 1. **Convention Over Configuration**
Projects follow a standardized structure. This means:
- Onboarding new team members is faster
- Code reviews focus on business logic, not project setup
- Switching between projects feels familiar

### 2. **Separation of Concerns**
Clear boundaries between different pipeline components:
- **Pipelines** orchestrate high-level workflow
- **Processors** handle Extract and Transform logic
- **Utilities** provide cross-cutting concerns (logging, sessions, timing)
- **Config** centralizes table and database definitions

### 3. **Developer Experience First**
- Edit dependencies in Python, not TOML
- Automatic import registration
- CLI-driven scaffolding reduces copy-paste errors
- Framework files marked "DO NOT MODIFY" for clarity

### 4. **Production-Ready from Day One**
- Singleton ETL pattern prevents session leaks
- Structured logging with context and timestamps
- Performance timing decorators built-in
- Git integration and proper versioning

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

### Using pipx (Recommended)

```bash
pipx install pypeline-cli
```

### Using pip

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

### Step 5: Create Processors

Processors handle the Extract and Transform logic. Create a processor for each data source or transformation concern:

```bash
pypeline create-processor --name sales-extractor --pipeline customer-segmentation
pypeline create-processor --name customer-enrichment --pipeline customer-segmentation
pypeline create-processor --name segmentation-logic --pipeline customer-segmentation
```

Each processor is scaffolded with:
- `__init__()` method for data extraction
- `process()` method for transformations
- Logger and ETL utilities auto-instantiated
- Unit test file with pytest fixtures

### Step 6: Implement Processor Logic

Edit `customer_analytics/pipelines/customer_segmentation/processors/sales_extractor_processor.py`:

```python
from typing import Final
from snowflake.snowpark import DataFrame
from snowflake.snowpark.functions import col, sum as sum_, count

from ....utils.etl import ETL
from ....utils.logger import Logger
from ....utils.decorators import time_function
from ..config import SALES_MONTHLY  # Import from pipeline config

MODULE_NAME: Final[str] = "pipelines/customer_segmentation/processors/sales_extractor_processor.py"


class SalesExtractorProcessor:
    """
    Extracts sales data from monthly partitioned tables.

    This processor reads from the SALES_MONTHLY table configuration and
    performs initial transformations to prepare data for enrichment.
    """

    def __init__(self, month: int):
        """
        Initialize and extract sales data for specified month.

        Args:
            month: Month number (1-12) to extract
        """
        self.logger = Logger()
        self.etl = ETL()
        self.month = month

        # Extract: Read from Snowflake using TableConfig
        SALES_MONTHLY.month = month
        table_name = SALES_MONTHLY.generate_table_name()

        self.logger.info(
            message=f"Extracting sales data from {table_name}",
            context=MODULE_NAME
        )

        self.raw_sales_df = self.etl.session.table(table_name)

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

        # Apply transformations
        df = self._filter_valid_transactions()
        df = self._aggregate_by_customer()
        df = self._calculate_metrics(df)

        return df

    def _filter_valid_transactions(self) -> DataFrame:
        """
        Filter out invalid or cancelled transactions.

        Returns:
            Filtered DataFrame
        """
        return self.raw_sales_df.filter(
            (col("STATUS") == "COMPLETED") &
            (col("AMOUNT") > 0)
        )

    def _aggregate_by_customer(self) -> DataFrame:
        """
        Aggregate sales metrics by customer.

        Returns:
            DataFrame with customer-level aggregates
        """
        return self.raw_sales_df.group_by("CUSTOMER_ID").agg(
            sum_("AMOUNT").alias("TOTAL_SALES"),
            count("TRANSACTION_ID").alias("TRANSACTION_COUNT")
        )

    def _calculate_metrics(self, df: DataFrame) -> DataFrame:
        """
        Calculate derived metrics like average order value.

        Args:
            df: Aggregated DataFrame

        Returns:
            DataFrame with calculated metrics
        """
        return df.with_column(
            "AVG_ORDER_VALUE",
            col("TOTAL_SALES") / col("TRANSACTION_COUNT")
        )
```

### Step 7: Wire Processors in Pipeline Runner

Edit `customer_analytics/pipelines/customer_segmentation/customer_segmentation_runner.py`:

```python
from pathlib import Path
from typing import Final, Literal

from snowflake.snowpark import DataFrame

from ...utils.etl import ETL
from ...utils.logger import Logger
from ...utils.decorators import time_function

# Import processors (auto-added by create-processor command)
from .processors.sales_extractor_processor import SalesExtractorProcessor
from .processors.customer_enrichment_processor import CustomerEnrichmentProcessor
from .processors.segmentation_logic_processor import SegmentationLogicProcessor

MODULE_NAME: Final[str] = Path(__file__).name


class CustomerSegmentationPipeline:
    """
    Customer segmentation pipeline.

    Extracts sales data, enriches with customer attributes, and applies
    segmentation logic to classify customers into segments.
    """

    def __init__(self, month: int):
        """
        Initialize pipeline.

        Args:
            month: Month to process (1-12)
        """
        self.logger = Logger()
        self.etl = ETL()
        self.month = month

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
        df: DataFrame = self.run_processors()

        if _write:
            table_path = f"PRODUCTION.ANALYTICS.customer_segments_{self.month:02d}"
            self._write_to_snowflake(df, write_mode="overwrite", table_path=table_path)

    def run_processors(self) -> DataFrame:
        """
        Instantiate and run processors in sequence.

        Returns:
            Final DataFrame with customer segments
        """
        # Extract sales data
        sales_processor = SalesExtractorProcessor(month=self.month)
        sales_df = sales_processor.process()

        # Enrich with customer data
        enrichment_processor = CustomerEnrichmentProcessor(sales_df=sales_df)
        enriched_df = enrichment_processor.process()

        # Apply segmentation logic
        segmentation_processor = SegmentationLogicProcessor(enriched_df=enriched_df)
        segmented_df = segmentation_processor.process()

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

### Step 8: Run Your Pipeline

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the pipeline
python -m customer_analytics.pipelines.customer_segmentation.customer_segmentation_runner
```

Or import and run programmatically:

```python
from customer_analytics import CustomerSegmentationPipeline

pipeline = CustomerSegmentationPipeline(month=3)
pipeline.run(_write=True)
```

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
- Project directory with src-layout
- Git repository with initial commit (if `--git` flag used)
- `pyproject.toml` with either:
  - Git-based versioning (if `--git`): Uses hatch-vcs, version from git tags
  - Manual versioning (if `--no-git`): Static version "0.1.0"
- Utility modules in `{project}/utils/`
- Test directory structure
- `dependencies.py` for dependency management
- LICENSE file
- `.gitignore` and optionally `.gitattributes` (if using git)

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

**Upload to Snowflake:**
```sql
-- From SnowSQL or Snowflake worksheet
PUT file://dist/snowflake/my_project-0.1.0.zip @your_stage AUTO_COMPRESS=FALSE;

-- Verify upload
LIST @your_stage;

-- Use in Snowpark procedure or UDF
CREATE OR REPLACE PROCEDURE run_customer_segmentation()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.12'
PACKAGES = ('snowflake-snowpark-python')
IMPORTS = ('@your_stage/my_project-0.1.0.zip')
HANDLER = 'my_project.pipelines.customer_segmentation.customer_segmentation_runner.CustomerSegmentationPipeline.run';
```

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

pypeline-cli follows a **Processor Pattern** for organizing ETL logic:

```
Pipeline (Orchestrator)
    ↓
Processor 1 (Extract + Transform)
    ↓
Processor 2 (Transform)
    ↓
Processor 3 (Transform)
    ↓
Pipeline (Load)
```

**Key Principles:**

1. **Extraction happens in `__init__()`**
   - Processors extract data during instantiation
   - Store raw data as instance attributes
   - Use TableConfig for dynamic table names

2. **Transformation happens in `process()`**
   - Main orchestrator method
   - Calls private transformation methods
   - Returns final DataFrame

3. **Loading happens in Pipeline Runner**
   - Pipeline orchestrates all processors
   - Pipeline handles final write to Snowflake
   - Conditional writes based on `_write` flag

### Extract, Transform, Load (ETL) Stages

#### **Stage 1: Extract**

**Where:** Processor `__init__()` method

**Purpose:** Read data from source(s) into DataFrames

**Best Practices:**
- Use `TableConfig` for dynamic table names
- Store extracted DataFrames as instance attributes
- Log table names and row counts
- Handle missing tables gracefully

**Example:**

```python
class OrdersExtractorProcessor:
    def __init__(self, year: int, month: int):
        self.logger = Logger()
        self.etl = ETL()

        # Configure table for monthly partition
        ORDERS_TABLE.month = month
        table_name = ORDERS_TABLE.generate_table_name(year=year)

        self.logger.info(
            message=f"Extracting orders from {table_name}",
            context=MODULE_NAME
        )

        # Extract: Read from Snowflake
        self.orders_df = self.etl.session.table(table_name)

        # Log extraction metrics
        row_count = self.orders_df.count()
        self.logger.info(
            message=f"Extracted {row_count} orders",
            context=MODULE_NAME
        )
```

**Architecture Diagram:**

```
┌─────────────────────────────────────┐
│  Processor.__init__()               │
├─────────────────────────────────────┤
│ 1. Get TableConfig                  │
│ 2. Generate table name              │
│ 3. Read from Snowflake              │
│ 4. Store as instance attribute      │
│ 5. Log extraction metrics           │
└─────────────────────────────────────┘
         │
         ▼
   self.orders_df (DataFrame)
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
class OrdersExtractorProcessor:
    # ... __init__ above ...

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
        Join customer tier from CUSTOMER_DIM table.

        Adds CUSTOMER_TIER column based on lifetime value.
        """
        customer_dim_table = CUSTOMER_DIM.generate_table_name()
        customer_df = self.etl.session.table(customer_dim_table)

        return df.join(
            customer_df.select("CUSTOMER_ID", "CUSTOMER_TIER"),
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
│  Processor.process()                   │
├────────────────────────────────────────┤
│  1. _filter_completed_orders()         │
│       │                                 │
│       ▼                                 │
│  2. _calculate_order_totals(df)        │
│       │                                 │
│       ▼                                 │
│  3. _enrich_customer_tier(df)          │
│       │                                 │
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
│                    PIPELINE ORCHESTRATOR                        │
│                                                                 │
│  run(_write: bool)                                              │
│    │                                                             │
│    ▼                                                             │
│  pipeline(_write)                                               │
│    │                                                             │
│    ▼                                                             │
│  run_processors()                                               │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSOR 1: EXTRACT                         │
│                                                                 │
│  __init__():                                                    │
│    - Get TableConfig                                            │
│    - Generate table name                                        │
│    - Read from Snowflake                                        │
│    - Store as self.df                                           │
│                                                                 │
│  process():                                                     │
│    - _filter_valid_rows()                                       │
│    - _calculate_metrics()                                       │
│    - return df                                                  │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSOR 2: TRANSFORM                       │
│                                                                 │
│  __init__(df):                                                  │
│    - Store input df                                             │
│                                                                 │
│  process():                                                     │
│    - _enrich_with_lookup()                                      │
│    - _apply_business_rules()                                    │
│    - return df                                                  │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSOR 3: AGGREGATE                       │
│                                                                 │
│  __init__(df):                                                  │
│    - Store input df                                             │
│                                                                 │
│  process():                                                     │
│    - _group_by_dimensions()                                     │
│    - _calculate_aggregates()                                    │
│    - return final_df                                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE: LOAD                               │
│                                                                 │
│  if _write:                                                     │
│    _write_to_snowflake(df, "overwrite", "DB.SCHEMA.TABLE")    │
│      │                                                           │
│      ▼                                                           │
│    df.write.mode("overwrite").save_as_table("DB.SCHEMA.TABLE") │
│                                                                 │
│  Log completion                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Built-in Utilities

pypeline-cli provides several utility modules out-of-the-box. These are auto-generated in `{project}/utils/`.

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
