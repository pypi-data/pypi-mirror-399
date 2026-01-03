import click
import sys
from typing import Optional

from iceberg_cli.profiles import ProfileManager
from iceberg_cli.catalog import (
    get_catalog, 
    list_namespaces, 
    list_tables, 
    get_table, 
    create_namespace, 
    drop_namespace,
    drop_table,
    create_table
)
from iceberg_cli.sql import execute_query
from iceberg_cli.schema_parser import parse_schema_string
from iceberg_cli.utils import print_error, print_success, print_info, print_json, print_table
from iceberg_cli.documentation import HELP_TEXT
from rich.markdown import Markdown
from rich.console import Console
from iceberg_cli.shell import IcebergShell

@click.group()
@click.option('--profile', '-p', help='Catalog profile to use.')
@click.pass_context
def cli(ctx, profile):
    """Iceberg CLI: Manage and Query Iceberg REST Catalogs."""
    ctx.ensure_object(dict)
    ctx.ensure_object(dict)
    ctx.obj['PROFILE'] = profile

@cli.command(name="docs")
def docs_cmd():
    """Show built-in documentation and usage guide."""
    console = Console()
    console.print(Markdown(HELP_TEXT))

@cli.command(name="shell")
def shell_cmd():
    """Start interactive shell (REPL)."""
    IcebergShell().cmdloop()

@cli.command(name="completion")
@click.argument("shell", type=click.Choice(['bash', 'zsh', 'fish']), default='bash')
def completion_cmd(shell):
    """Generate shell completion script."""
    # Click 8.x+ has shell_completion support
    # User needs to eval this output.
    # We output a helpful guide + the command
    
    prog_name = "iceberg" # The installed script name
    
    if shell == 'bash':
        click.echo(f"# Put this in your .bashrc:\n# eval \"$(_ICEBERG_COMPLETE=bash_source {prog_name})\"")
    elif shell == 'zsh':
        click.echo(f"# Put this in your .zshrc:\n# eval \"$(_ICEBERG_COMPLETE=zsh_source {prog_name})\"")
    elif shell == 'fish':
        click.echo(f"# Put this in your config.fish:\n# eval \"$(_ICEBERG_COMPLETE=fish_source {prog_name})\"")

@cli.command(name="upload")
@click.argument("file_path")
@click.argument("identifier")
@click.option("--file-format", type=click.Choice(['csv', 'parquet', 'json']), help="Force file format (default: infer from extension)")
@click.pass_context
def upload_cmd(ctx, file_path, identifier, file_format):
    """Upload a file (CSV, Parquet, JSON) as an Iceberg table."""
    profile_name = ctx.obj.get('PROFILE')
    
    try:
        import pyarrow.csv as pa_csv
        import pyarrow.parquet as pa_parquet
        import pyarrow.json as pa_json
        import pyarrow as pa
        from pyiceberg.exceptions import NoSuchTableError
    except ImportError:
        print_error("PyArrow is required for upload. Please install it.")
        sys.exit(1)

    catalog = get_catalog(profile_name)

    # 1. Infer Format
    if not file_format:
        if file_path.endswith('.csv'): file_format = 'csv'
        elif file_path.endswith('.parquet'): file_format = 'parquet'
        elif file_path.endswith('.json'): file_format = 'json'
        else:
            print_error("Could not infer format. Use --file-format.")
            sys.exit(1)

    # 2. Read File to Arrow Table
    try:
        if file_format == 'csv':
            arrow_table = pa_csv.read_csv(file_path)
        elif file_format == 'parquet':
            arrow_table = pa_parquet.read_table(file_path)
        elif file_format == 'json':
            arrow_table = pa_json.read_json(file_path)
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        sys.exit(1)

    # 3. Get or Create Table
    try:
        try:
            table = catalog.load_table(identifier)
            print_info(f"Table '{identifier}' exists. Appending data...")
        except NoSuchTableError:
            print_info(f"Table '{identifier}' does not exist. Creating from file schema...")
            table = catalog.create_table(identifier, schema=arrow_table.schema)
            print_success(f"Table '{identifier}' created.")

        # 4. Append Data
        table.append(arrow_table)
        print_success(f"Successfully uploaded {arrow_table.num_rows} rows to '{identifier}'.")

    except Exception as e:
        print_error(f"Upload failed: {e}")
        sys.exit(1)



# --- Profile Management ---
@cli.group()
def profile():
    """Manage catalog profiles."""
    pass

@profile.command(name="list")
def list_profiles_cmd():
    """List all configured profiles."""
    mgr = ProfileManager()
    profiles = mgr.list_profiles()
    
    rows = []
    for name, conf in profiles.items():
        uri = conf.get("uri", "N/A")
        rows.append([name, uri])
    
    print_table("Profiles", ["Name", "URI"], rows)

@profile.command(name="add")
@click.argument("name")
@click.option("--uri", required=True, help="Catalog URI")
@click.option("--set", "config_options", multiple=True, help="Additional config KEY=VALUE")
def add_profile_cmd(name, uri, config_options):
    """Add or update a catalog profile."""
    mgr = ProfileManager()
    
    extra_config = {}
    for item in config_options:
        if "=" in item:
            k, v = item.split("=", 1)
            extra_config[k] = v
        else:
            print_error(f"Invalid config format: {item}. Use KEY=VALUE.")
            sys.exit(1)
            
    if mgr.add_profile(name, uri, extra_config):
        print_success(f"Profile '{name}' added/updated.")
    else:
        sys.exit(1)

        sys.exit(1)

@profile.command(name="update")
@click.argument("name")
@click.option("--uri", required=False, help="New Catalog URI")
@click.option("--set", "config_options", multiple=True, help="Update config KEY=VALUE")
def update_profile_cmd(name, uri, config_options):
    """Update an existing profile (partial update)."""
    mgr = ProfileManager()
    
    extra_config = {}
    for item in config_options:
        if "=" in item:
            k, v = item.split("=", 1)
            extra_config[k] = v
        else:
            print_error(f"Invalid config format: {item}. Use KEY=VALUE.")
            sys.exit(1)
            
    if mgr.update_profile(name, uri, extra_config):
        print_success(f"Profile '{name}' updated.")
    else:
        print_error(f"Profile '{name}' not found or update failed.")
        sys.exit(1)
@profile.command(name="remove")
@click.argument("name")
def remove_profile_cmd(name):
    """Remove a profile."""
    mgr = ProfileManager()
    if mgr.remove_profile(name):
        print_success(f"Profile '{name}' removed.")
    else:
        print_error(f"Profile '{name}' not found.")
        sys.exit(1)

@profile.command(name="rename")
@click.argument("old_name")
@click.argument("new_name")
def rename_profile_cmd(old_name, new_name):
    """Rename a profile."""
    mgr = ProfileManager()
    if mgr.rename_profile(old_name, new_name):
        print_success(f"Profile '{old_name}' renamed to '{new_name}'.")
    else:
        print_error(f"Failed to rename '{old_name}' to '{new_name}'. (Check if old exists and new does not).")
        sys.exit(1)

# --- Catalog Operations ---
@cli.command(name="list")
@click.argument("namespace", required=False)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_cmd(ctx, namespace, as_json):
    """List namespaces or tables."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        
        if namespace:
            # List tables in this namespace
            tables = list_tables(catalog, namespace)
            if tables:
                formatted_rows = [".".join(t) for t in tables]
                if as_json:
                    print_json(formatted_rows)
                else:
                    data = [[r] for r in formatted_rows]
                    print_table(f"Tables in {namespace}", ["Identifier"], data)
            else:
                if as_json: print_json([])
                else: print_info(f"No tables found in {namespace} (or namespace empty).")
        else:
            # List namespaces at root
            namespaces = list_namespaces(catalog)
            if namespaces:
                formatted_rows = [".".join(ns) for ns in namespaces]
                if as_json:
                    print_json(formatted_rows)
                else:
                    data = [[r] for r in formatted_rows]
                    print_table("Namespaces", ["Namespace"], data)
            else:
                if as_json: print_json([])
                else: print_info("No namespaces found.")
                
    except Exception as e:
        if as_json: print_json({"error": str(e)})
        else: sys.exit(1)

@cli.command(name="describe")
@click.argument("table_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def describe_cmd(ctx, table_id, as_json):
    """Show table schema and metadata."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, table_id)
        if table:
            # Gather data
            data = {
                "identifier": table_id,
                "location": table.location(),
                "schema": [],
                "partition_spec": []
            }
            
            schema = table.schema()
            data["schema"] = [{"id": f.field_id, "name": f.name, "type": str(f.field_type), "required": f.required} for f in schema.fields]
            
            spec = table.spec()
            if spec.fields:
                data["partition_spec"] = [{"field_id": f.field_id, "name": f.name, "transform": str(f.transform)} for f in spec.fields]
            
            if as_json:
                print_json(data)
                return

            # Print basic info
            print_info(f"Table Location: {data['location']}")
            
            if spec.fields:
                data["partition_spec"] = [{"field_id": f.field_id, "name": f.name, "transform": str(f.transform)} for f in spec.fields]
            
            # --- Enhanced: Properties & Snapshot ---
            data["properties"] = table.properties
            
            data["current_snapshot"] = None
            if table.current_snapshot():
                snap = table.current_snapshot()
                data["current_snapshot"] = {
                    "id": snap.snapshot_id,
                    "timestamp": snap.timestamp_ms,
                    "operation": snap.summary.get("operation")
                }

            if as_json:
                print_json(data)
                return

            # Print basic info
            print_info(f"Table Location: {data['location']}")
            
            # Print Schema
            rows = [[str(f['id']), f['name'], f['type'], str(f['required'])] for f in data['schema']]
            print_table(f"Schema: {table_id}", ["ID", "Name", "Type", "Required"], rows)
            
            # Print Partition Spec
            if data["partition_spec"]:
                spec_rows = [[str(f['field_id']), f['name'], f['transform']] for f in data['partition_spec']]
                print_table("Partition Spec", ["Field ID", "Name", "Transform"], spec_rows)
            
            # Print Properties (Enhanced)
            if data["properties"]:
                prop_rows = [[k, v] for k, v in data["properties"].items()]
                print_table("Table Properties", ["Key", "Value"], prop_rows)

            # Print Snapshot Summary (Enhanced)
            if data["current_snapshot"]:
                snap = data["current_snapshot"]
                snap_rows = [[str(snap["id"]), str(snap["timestamp"]), str(snap["operation"])]]
                print_table("Current Snapshot", ["ID", "Timestamp", "Operation"], snap_rows)
            else:
                print_info("No current snapshot.")
                
    except Exception as e:
        if as_json: print_json({"error": str(e)})
        else: sys.exit(1)

@cli.command(name="query")
@click.argument("sql_query")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def query_cmd(ctx, sql_query, as_json):
    """Run a SQL query using DataFusion."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        headers, rows = execute_query(catalog, sql_query)
        
        if as_json:
            print_json(rows if rows else [])
            return

        if rows:
            MAX_ROWS = 100
            display_rows = []
            for i, row in enumerate(rows):
                if i >= MAX_ROWS: break
                display_rows.append([str(row[h]) for h in headers])
            
            print_table(f"Results ({len(rows)} rows)", headers, display_rows)
            if len(rows) > MAX_ROWS:
                print_info(f"Output truncated at {MAX_ROWS} rows.")
        else:
            print_info("Query returned no results.")
            
    except Exception as e:
        if as_json: print_json({"error": str(e)})
        else: sys.exit(1)
        
@cli.command(name="files")
@click.argument("table_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def files_cmd(ctx, table_id, as_json):
    """List data files in the current snapshot."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, table_id)
        if table:
            scan = table.scan()
            tasks = scan.plan_files()
            file_list = []
            
            for task in tasks:
                 file_list.append({
                     "path": task.file.file_path,
                     "format": str(task.file.file_format),
                     "records": task.file.record_count
                 })
            
            if as_json:
                print_json(file_list)
                return

            rows = [[f["path"], f["format"], str(f["records"])] for f in file_list]
            display_rows = rows[:100]
            print_table(f"Files in {table_id}", ["Path", "Format", "Records"], display_rows)
            if len(rows) > 100:
                print_info(f"Showing 100 of {len(rows)} files.")

    except Exception as e:
        if as_json: print_json({"error": str(e)})
        else: sys.exit(1)

# --- Create/Drop Commands ---
@cli.group()
def create():
    """Create resources."""
    pass

@create.command(name="namespace")
@click.argument("namespace")
@click.option("--property", "-p", multiple=True, help="Property KEY=VALUE")
@click.pass_context
def create_ns_cmd(ctx, namespace, property):
    """Create a namespace."""
    profile_name = ctx.obj.get('PROFILE')
    catalog = get_catalog(profile_name)
    props = {}
    for p in property:
        k, v = p.split("=", 1)
        props[k] = v
        
    if create_namespace(catalog, namespace, props):
        print_success(f"Namespace '{namespace}' created.")

@create.command(name="table")
@click.argument("identifier")
@click.option("--schema", required=True, help="Schema string (e.g. 'id int, name string')")
@click.option("--property", "-p", multiple=True, help="Property KEY=VALUE")
@click.pass_context
def create_table_cmd(ctx, identifier, schema, property):
    """Create a table with a simple schema."""
    profile_name = ctx.obj.get('PROFILE')
    catalog = get_catalog(profile_name)
    
    # Parse props
    props = {}
    for p in property:
        if "=" in p:
            k, v = p.split("=", 1)
            props[k] = v
            
    try:
        pa_schema = parse_schema_string(schema)
        if create_table(catalog, identifier, pa_schema, props):
            print_success(f"Table '{identifier}' created.")
    except Exception as e:
        print_error(str(e))

@cli.group()
def drop():
    """Drop resources."""
    pass

@cli.group()
def maintenance():
    """Table maintenance operations."""
    pass

@maintenance.command(name="expire-snapshots")
@click.argument("identifier")
@click.option("--retain-last", type=int, help="Number of snapshots to retain", default=1)
@click.pass_context
def expire_snapshots_cmd(ctx, identifier, retain_last):
    """Expire old snapshots."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, identifier)
        if table:
            # PyIceberg expire_snapshots is not fully exposing a 'retain_last' integer directly in all versions 
            # OR it might work via specific API.
            # Table.expire_snapshots() returns an ExpireSnapshots action builder.
            # We call expire_older_than(...) or retain_last(...)
            print_info(f"Expiring snapshots for {identifier}...")
            # Note: pyiceberg action API might differ by version. 
            # Checking standard usage: table.expire_snapshots().retain_last(n).commit()
            table.expire_snapshots().retain_last(retain_last).commit()
            print_success("Snapshots expired.")
    except Exception as e:
        print_error(f"Maintenance failed: {e}")

@maintenance.command(name="remove-orphans")
@click.argument("identifier")
@click.pass_context
def remove_orphans_cmd(ctx, identifier):
    """Remove orphan files (Not fully supported in vanilla PyIceberg yet)."""
    # PyIceberg does NOT have a comprehensive remove_orphan_files action in the open source core recently?
    # Actually it might be there or coming. If not, we warn.
    # It is often engine dependent. 
    print_error("Remove orphans is not yet supported in this CLI version (waiting for PyIceberg support).")

@cli.group()
def properties():
    """Manage table properties."""
    pass

@properties.command(name="set")
@click.argument("identifier")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_prop_cmd(ctx, identifier, key, value):
    """Set a table property."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, identifier)
        if table:
            with table.transaction() as txn:
                txn.set_properties({key: value})
            print_success(f"Property '{key}' set to '{value}'.")
    except Exception as e:
        print_error(f"Failed to set property: {e}")

@properties.command(name="remove")
@click.argument("identifier")
@click.argument("key")
@click.pass_context
def remove_prop_cmd(ctx, identifier, key):
    """Remove a table property."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, identifier)
        if table:
            with table.transaction() as txn:
                txn.remove_properties(key)
            print_success(f"Property '{key}' removed.")
    except Exception as e:
        print_error(f"Failed to remove property: {e}")


@drop.command(name="namespace")
@click.argument("namespace")
@click.pass_context
def drop_ns_cmd(ctx, namespace):
    """Drop a namespace."""
    profile_name = ctx.obj.get('PROFILE')
    catalog = get_catalog(profile_name)
    if drop_namespace(catalog, namespace):
        print_success(f"Namespace '{namespace}' dropped.")

@drop.command(name="table")
@click.argument("identifier")
@click.pass_context
def drop_table_cmd(ctx, identifier):
    """Drop a table."""
    profile_name = ctx.obj.get('PROFILE')
    catalog = get_catalog(profile_name)
    if drop_table(catalog, identifier):
        print_success(f"Table '{identifier}' dropped.")

# --- Metadata Inspection ---
@cli.command(name="metadata")
@click.argument("meta_type", type=click.Choice(['history', 'snapshots', 'manifests'], case_sensitive=False))
@click.argument("table_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def metadata_cmd(ctx, meta_type, table_id, as_json):
    """Inspect table metadata (history, snapshots, manifests)."""
    profile_name = ctx.obj.get('PROFILE')
    try:
        catalog = get_catalog(profile_name)
        table = get_table(catalog, table_id)
        if not table: return

        data = []
        if meta_type == 'history':
            data = [{"timestamp": h.timestamp_ms, "snapshot_id": h.snapshot_id} for h in table.history()]
            if as_json:
                print_json(data)
                return
            rows = [[str(d["timestamp"]), str(d["snapshot_id"])] for d in data]
            print_table("History", ["Timestamp", "Snapshot ID"], rows)
        
        elif meta_type == 'snapshots':
            data = [{"snapshot_id": s.snapshot_id, "timestamp": s.timestamp_ms, "manifest_list": s.manifest_list} for s in table.snapshots()]
            if as_json:
                print_json(data)
                return
            rows = [[str(d["snapshot_id"]), str(d["timestamp"]), d["manifest_list"]] for d in data]
            print_table("Snapshots", ["ID", "Timestamp", "Manifest List"], rows)
            
        elif meta_type == 'manifests':
             if table.current_snapshot():
                 m_list = table.current_snapshot().manifest_list
                 if as_json:
                     print_json({"manifest_list": m_list})
                     return
                 print_info(f"Manifest List: {m_list}")
             else:
                 if as_json: print_json({})
                 else: print_info("No current snapshot.")

    except Exception as e:
        if as_json: print_json({"error": str(e)})
        else: 
            print_error(f"Failed to inspect metadata: {e}")

if __name__ == '__main__':
    cli()
