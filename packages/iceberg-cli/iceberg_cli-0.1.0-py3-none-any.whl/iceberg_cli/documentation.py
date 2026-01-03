HELP_TEXT = """
# Iceberg CLI Documentation

Welcome to the **Iceberg REST CLI**. This tool allows you to manage PyIceberg configuration, interact with catalogs, upload data, and query tables using DataFusion.

## Profile Management

Configure connection details in `~/.pyiceberg.yaml`.

- **List Profiles**:
  `iceberg profile list`

- **Add a Profile**:
  `iceberg profile add <name> --uri <uri> --set token=... --set warehouse=...`
  
- **Update a Profile**:
  `iceberg profile update <name> --set token=new_token`
  
- **Rename a Profile**:
  `iceberg profile rename <old> <new>`

- **Remove a Profile**:
  `iceberg profile remove <name>`

## Catalog Operations

- **List Namespaces**:
  `iceberg list`

- **List Tables**:
  `iceberg list <namespace>`

- **Create Resources**:
  `iceberg create namespace <ns>`
  `iceberg create table <ns>.<table> --schema "id int, name string"`

- **Drop Resources**:
  `iceberg drop namespace <ns>`
  `iceberg drop table <ns>.<table>`

## Data Operations

- **Upload Data**:
  `iceberg upload <file_path> <table_identifier>`
  Support CSV, Parquet, JSON. (Creates table if not exists).

- **Query Data (SQL)**:
  `iceberg query "SELECT * FROM <ns>.<table> LIMIT 5"`
  
- **List Files**:
  `iceberg files <table>`

## Table Maintenance & Metadata

- **Describe Table**:
  `iceberg describe <table>` (Shows schema, properties, current snapshot)

- **Metadata Inspection**:
  `iceberg metadata history <table>`
  `iceberg metadata snapshots <table>`
  
- **Maintenance**:
  `iceberg maintenance expire-snapshots <table> --retain-last 5`

## Utilities

- **Interactive Shell**:
  `iceberg shell` (Start REPL)

- **JSON Output**:
  Add `--json` to `list`, `query`, `describe`, `files`, or `metadata` for machine-readable output.

- **Autocompletion**:
  `iceberg completion bash` (Generate shell script)

For more help on a specific command, use `--help` (e.g., `iceberg profile add --help`).
"""
