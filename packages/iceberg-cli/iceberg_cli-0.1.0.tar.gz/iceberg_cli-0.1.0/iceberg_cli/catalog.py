from typing import List, Dict, Any, Optional, Union
from pyiceberg.catalog import load_catalog, Catalog
from pyiceberg.table import Table
from pyiceberg.exceptions import NoSuchTableError, NoSuchNamespaceError, NamespaceAlreadyExistsError, TableAlreadyExistsError
from iceberg_cli.utils import print_error
import pyarrow as pa

def get_catalog(name: Optional[str] = None) -> Catalog:
    """
    Loads the catalog. If name is None, pyiceberg loads the default from config.
    """
    try:
        return load_catalog(name)
    except Exception as e:
        # Fallback or error handling
        if name:
             print_error(f"Could not load catalog '{name}'. Check your configuration ({e}).")
        else:
             print_error(f"Could not load default catalog. Check your ~/.pyiceberg.yaml ({e}).")
        raise

def list_namespaces(catalog: Catalog, parent: Optional[str] = None) -> List[tuple]:
    """
    Lists namespaces. Returns a list of namespace identifiers (tuples).
    """
    try:
        if parent:
            return catalog.list_namespaces(parent)
        return catalog.list_namespaces()
    except NoSuchNamespaceError:
        print_error(f"Namespace '{parent}' not found.")
        return []

def list_tables(catalog: Catalog, namespace: str) -> List[tuple]:
    """
    Lists tables in a namespace.
    """
    try:
        return catalog.list_tables(namespace)
    except NoSuchNamespaceError:
        print_error(f"Namespace '{namespace}' not found.")
        return []

def get_table(catalog: Catalog, identifier: str) -> Optional[Table]:
    """
    Loads a table.
    """
    try:
        return catalog.load_table(identifier)
    except NoSuchTableError:
        print_error(f"Table '{identifier}' not found.")
        return None
    except Exception as e:
        print_error(f"Error loading table '{identifier}': {e}")
        return None

def create_namespace(catalog: Catalog, namespace: str, properties: Dict[str, str] = None):
    try:
        catalog.create_namespace(namespace, properties or {})
        return True
    except Exception as e:
        print_error(f"Failed to create namespace: {e}")
        return False

def drop_namespace(catalog: Catalog, namespace: str):
    try:
        catalog.drop_namespace(namespace)
        return True
    except Exception as e:
        print_error(f"Failed to drop namespace: {e}")
        return False

def drop_table(catalog: Catalog, identifier: str):
    try:
        catalog.drop_table(identifier)
        return True
    except Exception as e:
        print_error(f"Failed to drop table: {e}")
        return False

def create_table(catalog: Catalog, identifier: str, schema: pa.Schema, properties: Dict[str, str] = None) -> bool:
    try:
        catalog.create_table(identifier, schema=schema, properties=properties or {})
        return True
    except TableAlreadyExistsError:
        print_error(f"Table '{identifier}' already exists.")
        return False
    except Exception as e:
        print_error(f"Failed to create table: {e}")
        return False
