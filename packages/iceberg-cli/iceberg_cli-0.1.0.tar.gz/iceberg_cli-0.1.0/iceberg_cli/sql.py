from typing import Optional
from pyiceberg.catalog import Catalog
from iceberg_cli.utils import print_error, print_table
import datafusion
import pyarrow

def execute_query(catalog: Catalog, sql: str):
    """
    Executes a SQL query against the catalog using DataFusion.
    Note: For this to work, we need to register tables involved in the query.
    
    Since we don't have an easy way to parse table names from SQL upfront without a parser,
    and we want to avoid loading *every* table in the catalog (too slow), 
    we rely on PyIceberg's DataFusion integration if it supports catalog-level registration,
    OR we make the user specify context, OR we try to infer.
    
    However, PyIceberg's `load_catalog` returns a catalog object. 
    Integration: As of recent versions, `pyiceberg` doesn't automatically expose a full catalog 
    to DataFusion as a single provider easily without some glue. 
    
    BUT, `pyiceberg` tables can be converted to Arrow, or registered individually.
    
    Strategy: 
    1. Parse the FROM clause? No, too brittle.
    2. Suggestion: `pyiceberg` tables act as DataFusion TableProviders.
    
    Wait, `pyiceberg` DOES have a `to_datafusion` or `scan().to_arrow()`...
    
    Actually, the best way currently with `pyiceberg[datafusion]` is using `ctx.register_table`.
    We will just register ALL tables mentioned? No.
    
    Limitation: We assume the user provides fully qualified names or we iterate known tables. 
    
    BETTER APPROACH for V1:
    The `iceberg query` command might fail if tables aren't registered. 
    We will create a helper that tries to identify tables in the query, OR 
    we ask the user to simplify.
    
    Actually, let's look at how PyIceberg docs suggest using DataFusion. 
    Usually: `ctx.register_table(name, pyiceberg_table)`.
    
    Algorithm:
    1. Create SessionContext.
    2. We need to find which tables are in the query.
    3. Naive text search for checking if known tables exist? 
       That requires listing all tables first, which is expensive.
       
    Alternative: We just tell the user "Tables must be fully qualified" and we try to regex catch them? 
    
    Let's try a simpler approach for now:
    We assume the query uses identifiers compatible with what we can load. 
    BUT DataFusion needs them registered BEFORE query.
    
    Workaround:
    We will regex parse `FROM <identifier>` and `JOIN <identifier>`.
    It's not perfect but good enough for a CLI v1.
    """
    import re
    
    # 1. Init Context
    ctx = datafusion.SessionContext()
    
    # 2. Naive regex to find potential table identifiers (namespace.table)
    # Matches words with dots, e.g., "ns.table", "ns.nested.table"
    # Avoiding basic SQL keywords.
    potential_tables = set(re.findall(r"[\w]+\.[\w]+(?:\.[\w]+)*", sql))
    
    registered_count = 0
    
    for identifier in potential_tables:
        try:
            table_obj = catalog.load_table(identifier)
            # Segfault mitigation: Convert to in-memory Arrow table
            # Direct registration of PyIceberg table objects can cause ABI issues
            arrow_table = table_obj.scan().to_arrow()
            
            # If identifier has namespace, create schema in DataFusion first
            if "." in identifier:
                ns = identifier.rsplit(".", 1)[0]
                # datafusion uses 'schema' concept. 
                # We simply try to create it.
                # Note: identifier might be "ns.nested.table". 
                # Datafusion supports "catalog.schema.table" or "schema.table".
                # We assume "schema.table" mapping for "ns.table".
                # If nested, we might just take the first part? 
                # Let's try to create the full prefix as a schema? No, schema is usually one level.
                # Simplification: we treat everything before the last dot as 'schema'.
                try:
                    ctx.sql(f"CREATE SCHEMA IF NOT EXISTS {ns}").collect()
                except Exception:
                    pass 

            # ctx.register_record_batches takes (name, partitions) where partitions is list of lists of batches
            # We treat the whole table as one partition
            ctx.register_record_batches(identifier, [arrow_table.to_batches()])
            registered_count += 1
        except Exception as e:
            print_error(f"Failed to register table '{identifier}': {e}")
            pass

    if registered_count == 0 and "SELECT" in sql.upper():
        print_error("No Iceberg tables detected in query or failed to load them. \nMake sure to use fully qualified names (e.g. `namespace.table`).")
        return

    # 3. Request
    try:
        df = ctx.sql(sql)
        # Convert to Arrow to print formatted table
        batches = df.collect()
        if not batches:
             return None, None

        # Return headers and row dicts
        tbl = pyarrow.Table.from_batches(batches)
        headers = tbl.column_names
        pylist = tbl.to_pylist()
        
        return headers, pylist
            
    except Exception as e:
        print_error(f"Query Execution Failed: {e}")
        return None, None
