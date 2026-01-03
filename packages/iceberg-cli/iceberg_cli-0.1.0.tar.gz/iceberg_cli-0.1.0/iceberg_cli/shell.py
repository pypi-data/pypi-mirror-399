import cmd
import shlex
import sys
from click.testing import CliRunner

class IcebergShell(cmd.Cmd):
    intro = 'Welcome to the Iceberg interactive shell. Type help or ? to list commands.\n'
    prompt = '(iceberg) '

    def do_list(self, arg):
        """List namespaces or tables: list [namespace]"""
        self._invoke("list", arg)

    def do_describe(self, arg):
        """Describe a table: describe <table_identifier>"""
        self._invoke("describe", arg)

    def do_query(self, arg):
        """Run a SQL query: query "SELECT ...\""""
        self._invoke("query", arg)

    def do_files(self, arg):
        """List files: files <table_identifier>"""
        self._invoke("files", arg)
    
    def do_metadata(self, arg):
        """View metadata: metadata <type> <table_identifier>"""
        self._invoke("metadata", arg)
        
    def do_profile(self, arg):
        """Profile commands: profile list|add|... """
        self._invoke("profile", arg)

    def do_create(self, arg):
        """Create resources: create namespace|table ..."""
        self._invoke("create", arg)
        
    def do_drop(self, arg):
        """Drop resources: drop namespace|table ..."""
        self._invoke("drop", arg)
    
    def do_upload(self, arg):
        """Upload a file: upload <file> <identifier>"""
        self._invoke("upload", arg)

    def do_exit(self, arg):
        """Exit the shell"""
        return True
        
    def do_quit(self, arg):
        """Exit the shell"""
        return True

    def _invoke(self, command, arg_str):
        # Defer import to avoid circular dependency with main.py
        from iceberg_cli.main import cli
        
        try:
            # We use "cli" object from main
            kwargs = {'standalone_mode': False}
            args = [command] + shlex.split(arg_str)
            cli.main(args=args, **kwargs)
            
        except SystemExit as e:
            if e.code != 0:
                print(f"Command returned exit code {e.code}")
        except Exception as e:
            print(f"Error: {e}")
