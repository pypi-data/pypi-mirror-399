# Iceberg CLI

A powerful, unified command-line interface for Apache Iceberg REST catalogs. This tool extends the capabilities of [PyIceberg](https://py.iceberg.apache.org/) with profile management, DataFusion SQL querying, and robust administrative tools.

## Documentation

**[-> View Full Documentation](./docs/README.md)**

## Installation

```bash
pip install iceberg-cli
```

### Storage Extras

```bash
pip install "iceberg-cli[s3]"   # AWS S3
pip install "iceberg-cli[adls]" # Azure Data Lake
pip install "iceberg-cli[gcs]"  # Google Cloud Storage
pip install "iceberg-cli[all]"  # All backends
```

## Quick Reference

| Feature | Command |
| :--- | :--- |
| **Profiles** | `iceberg profile list`, `add`, `update`, `rename`, `remove` |
| **Catalog** | `iceberg list`, `create`, `drop` |
| **Data** | `iceberg query`, `upload`, `files` |
| **Metadata** | `iceberg describe`, `metadata`, `maintenance` |
| **Shell** | `iceberg shell`, `completion` |

Run `iceberg docs` or `iceberg <command> --help` for details.
