"""
DVT CLI Entry Point Package

This standalone package provides the entry point for the DVT command-line
interface. It's separate from the 'dbt' namespace to avoid conflicts with
dbt-core during the initial import.

Why this package exists:
-----------------------
DVT extends dbt-core with additional commands (compute, target, migrate).
However, dbt adapters (like dbt-postgres) depend on dbt-core, so both
dvt-core and dbt-core end up installed together. Both packages provide
the 'dbt' namespace, which causes import conflicts.

The key issue is that both packages install files to the same location
(site-packages/dbt/). When dbt-core is installed after dvt-core, it
OVERWRITES DVT's files. This package detects this condition at runtime
and automatically restores DVT's files by reinstalling dvt-core.
"""

import subprocess
import sys
from pathlib import Path


def _check_dvt_cli_intact() -> bool:
    """
    Check if DVT's CLI is intact by looking for DVT-specific commands.

    Returns True if DVT's main.py is present (has --target-compute flag),
    False if dbt-core has overwritten it.
    """
    try:
        # Import the cli module
        from dbt.cli import main as cli_main

        # Check if DVT's signature command exists
        # DVT adds 'compute' group which dbt-core doesn't have
        if hasattr(cli_main, 'cli'):
            cli = cli_main.cli
            # Check for DVT-specific command groups
            # DVT adds: compute, target, migrate, profile, spark, java
            if hasattr(cli, 'commands'):
                commands = cli.commands
                # 'compute' command is DVT-specific
                return 'compute' in commands
            else:
                # Try invoking to check commands (older click pattern)
                import click
                if isinstance(cli, click.MultiCommand):
                    # Try to list commands
                    ctx = click.Context(cli)
                    cmds = cli.list_commands(ctx)
                    return 'compute' in cmds
        return False
    except Exception:
        return False


def _restore_dvt_files() -> bool:
    """
    Restore DVT's files by reinstalling dvt-core.

    This is called when dbt-core has overwritten DVT's files.
    We reinstall dvt-core with --no-deps to restore only DVT's files
    without affecting dbt-core (which adapters need for metadata).

    Tries multiple methods: uv, pip command, pip module.

    Returns True if restoration was successful.
    """
    import shutil

    print("  🔧 DVT: Restoring DVT files (dbt-core overwrote them)...", file=sys.stderr)

    # Method 1: Try uv (preferred - faster and more reliable)
    uv_path = shutil.which("uv")
    if uv_path:
        try:
            result = subprocess.run(
                [uv_path, "pip", "install", "--python", sys.executable,
                 "--reinstall", "--no-deps", "dvt-core", "--quiet"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  ✓ DVT files restored. Please re-run your command.", file=sys.stderr)
                return True
        except Exception:
            pass

    # Method 2: Try pip command
    pip_path = shutil.which("pip") or shutil.which("pip3")
    if pip_path:
        try:
            result = subprocess.run(
                [pip_path, "install", "--reinstall", "--no-deps",
                 "dvt-core", "--quiet"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  ✓ DVT files restored. Please re-run your command.", file=sys.stderr)
                return True
        except Exception:
            pass

    # Method 3: Try pip as Python module
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--reinstall",
             "--no-deps", "dvt-core", "--quiet"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  ✓ DVT files restored. Please re-run your command.", file=sys.stderr)
            return True
    except Exception:
        pass

    print("  ⚠ Failed to restore DVT files. Please run manually:", file=sys.stderr)
    print("     pip install --reinstall --no-deps dvt-core", file=sys.stderr)
    return False


def _clear_dbt_modules():
    """Clear cached dbt modules so they get reimported."""
    modules_to_clear = [k for k in list(sys.modules.keys()) if k.startswith('dbt')]
    for mod in modules_to_clear:
        del sys.modules[mod]


def dvt_cli():
    """
    DVT CLI entry point function.

    This is the main entry point for the 'dvt' command. It automatically
    detects if dbt-core has overwritten DVT's files and restores them.

    Users who want backward compatibility with 'dbt' command can create
    a shell alias: alias dbt=dvt
    """
    # Check if DVT's CLI is intact
    if not _check_dvt_cli_intact():
        # DVT's files have been overwritten by dbt-core
        # This happens when users install dbt adapters that depend on dbt-core
        if _restore_dvt_files():
            # Clear cached modules and exit - user needs to re-run
            _clear_dbt_modules()
            sys.exit(0)
        else:
            # Restoration failed, try to run anyway
            print("  ⚠ Could not restore DVT files. Some features may not work.", file=sys.stderr)

    # Import and run the CLI
    from dbt.cli.main import cli
    cli()
