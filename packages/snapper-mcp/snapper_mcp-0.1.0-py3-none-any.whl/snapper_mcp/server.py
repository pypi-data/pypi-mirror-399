#!/usr/bin/env python3
"""
BTRFS Snapper MCP Server

A Model Context Protocol server that exposes Snapper snapshot management
and BTRFS filesystem health monitoring through unified tools with action-based dispatch.

Environment Variables:
    SNAPPER_MCP_USE_SUDO: Set to "false" to disable sudo (default: "true")
    SNAPPER_MCP_SNAPPER_PATH: Path to snapper binary (default: "snapper")
    SNAPPER_MCP_BTRFS_PATH: Path to btrfs binary (default: "btrfs")
    SNAPPER_MCP_SUDO_PATH: Path to sudo binary (default: "sudo")
    SNAPPER_MCP_DEFAULT_CONFIG: Default snapper config name (default: "root")
    SNAPPER_MCP_DEFAULT_MOUNT: Default BTRFS mount point (default: "/")
    SNAPPER_MCP_TIMEOUT: Command timeout in seconds (default: "60")
"""

import asyncio
import json
import os
import subprocess
from enum import Enum
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field


# Configuration from environment variables
class Config:
    """Runtime configuration loaded from environment variables."""

    def __init__(self):
        self.use_sudo = os.environ.get("SNAPPER_MCP_USE_SUDO", "true").lower() == "true"
        self.snapper_path = os.environ.get("SNAPPER_MCP_SNAPPER_PATH", "snapper")
        self.btrfs_path = os.environ.get("SNAPPER_MCP_BTRFS_PATH", "btrfs")
        self.sudo_path = os.environ.get("SNAPPER_MCP_SUDO_PATH", "sudo")
        self.default_config = os.environ.get("SNAPPER_MCP_DEFAULT_CONFIG", "root")
        self.default_mount = os.environ.get("SNAPPER_MCP_DEFAULT_MOUNT", "/")
        self.timeout = int(os.environ.get("SNAPPER_MCP_TIMEOUT", "60"))

    def __repr__(self):
        return (
            f"Config(use_sudo={self.use_sudo}, snapper_path={self.snapper_path}, "
            f"btrfs_path={self.btrfs_path}, default_config={self.default_config}, "
            f"default_mount={self.default_mount}, timeout={self.timeout})"
        )


# Global config instance
config = Config()


class SnapperAction(str, Enum):
    """Available snapper actions."""
    LIST = "list"
    CREATE = "create"
    DELETE = "delete"
    ROLLBACK = "rollback"
    CLEANUP = "cleanup"
    DIFF = "diff"
    STATUS = "status"
    CONFIGS = "configs"


class SnapperArgs(BaseModel):
    """Arguments for the snapper tool."""
    action: SnapperAction = Field(
        description="The snapper action to perform: list (show snapshots), create (new snapshot), delete (remove snapshot), rollback (restore to snapshot), cleanup (prune by algorithm), diff (compare snapshots), status (show changed files), configs (list available configs)"
    )
    config: Optional[str] = Field(
        default=None,
        description="Snapper configuration name (e.g., 'root', 'home'). Uses default from SNAPPER_MCP_DEFAULT_CONFIG env var if not specified. Use 'configs' action to see available configs."
    )
    snapshot_id: Optional[int] = Field(
        default=None,
        description="Snapshot number for delete, rollback, or start of range for diff/status"
    )
    snapshot_id_end: Optional[int] = Field(
        default=None,
        description="End snapshot number for diff/status range (e.g., diff between snapshot 5 and 10)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description for new snapshot (used with 'create' action)"
    )
    cleanup_algorithm: Optional[str] = Field(
        default=None,
        description="Cleanup algorithm: 'number' (keep N snapshots), 'timeline' (keep by age), 'empty-pre-post' (remove empty pre/post pairs)"
    )
    sync_after_delete: bool = Field(
        default=True,
        description="Sync filesystem after delete operation"
    )

    def get_config(self) -> str:
        """Get the config name, falling back to default."""
        return self.config or config.default_config


def run_snapper_command(args: list[str], use_json: bool = False) -> tuple[bool, str, str]:
    """
    Execute a snapper command, optionally with sudo.

    Returns: (success, stdout, stderr)
    """
    cmd = []

    if config.use_sudo:
        cmd.append(config.sudo_path)

    cmd.append(config.snapper_path)

    if use_json:
        cmd.append("--jsonout")

    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {config.timeout} seconds"
    except FileNotFoundError as e:
        return False, "", f"Command not found: {e.filename}. Check SNAPPER_MCP_SNAPPER_PATH or SNAPPER_MCP_SUDO_PATH."
    except Exception as e:
        return False, "", str(e)


def handle_list(args: SnapperArgs) -> str:
    """List snapshots for a config."""
    cfg = args.get_config()
    success, stdout, stderr = run_snapper_command(
        ["-c", cfg, "list"],
        use_json=True
    )

    if not success:
        return f"Error listing snapshots: {stderr}"

    if not stdout.strip():
        return f"No snapshots found for config '{cfg}'"

    try:
        data = json.loads(stdout)
        # JSON output is wrapped: {"<config_name>": [...]}
        snapshots = data.get(cfg, [])
        if not snapshots:
            return f"No snapshots found for config '{cfg}'"

        # Format output nicely
        lines = [f"Snapshots for config '{cfg}':", ""]
        for snap in snapshots:
            num = snap.get("number", "?")
            snap_type = snap.get("type", "unknown")
            date = snap.get("date", "unknown")
            desc = snap.get("description", "")
            cleanup = snap.get("cleanup", "")

            line = f"  #{num} [{snap_type}] {date}"
            if desc:
                line += f" - {desc}"
            if cleanup:
                line += f" (cleanup: {cleanup})"
            lines.append(line)

        return "\n".join(lines)
    except json.JSONDecodeError:
        # Fallback to raw output
        return f"Snapshots for config '{cfg}':\n{stdout}"


def handle_create(args: SnapperArgs) -> str:
    """Create a new snapshot."""
    cfg = args.get_config()
    cmd = ["-c", cfg, "create", "--print-number"]

    if args.description:
        cmd.extend(["-d", args.description])

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error creating snapshot: {stderr}"

    snap_num = stdout.strip()
    desc_msg = f" with description '{args.description}'" if args.description else ""
    return f"Created snapshot #{snap_num} on config '{cfg}'{desc_msg}"


def handle_delete(args: SnapperArgs) -> str:
    """Delete a snapshot."""
    if args.snapshot_id is None:
        return "Error: snapshot_id is required for delete action"

    cfg = args.get_config()
    cmd = ["-c", cfg, "delete", str(args.snapshot_id)]

    if args.sync_after_delete:
        cmd.append("--sync")

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error deleting snapshot #{args.snapshot_id}: {stderr}"

    return f"Deleted snapshot #{args.snapshot_id} from config '{cfg}'"


def handle_rollback(args: SnapperArgs) -> str:
    """Rollback to a snapshot."""
    cfg = args.get_config()
    cmd = ["-c", cfg, "rollback", "--print-number"]

    if args.snapshot_id is not None:
        cmd.append(str(args.snapshot_id))

    if args.description:
        cmd.extend(["-d", args.description])

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error rolling back: {stderr}"

    snap_num = stdout.strip()
    target = f" to snapshot #{args.snapshot_id}" if args.snapshot_id else ""
    return f"Rollback{target} initiated. Created snapshot #{snap_num}. Reboot required to complete rollback."


def handle_cleanup(args: SnapperArgs) -> str:
    """Run cleanup/prune algorithm."""
    if not args.cleanup_algorithm:
        return "Error: cleanup_algorithm is required. Options: 'number', 'timeline', 'empty-pre-post'"

    cfg = args.get_config()
    cmd = ["-c", cfg, "cleanup", args.cleanup_algorithm]

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error running cleanup: {stderr}"

    return f"Cleanup '{args.cleanup_algorithm}' completed on config '{cfg}'"


def handle_diff(args: SnapperArgs) -> str:
    """Show diff between two snapshots."""
    if args.snapshot_id is None or args.snapshot_id_end is None:
        return "Error: Both snapshot_id and snapshot_id_end are required for diff action"

    cfg = args.get_config()
    cmd = ["-c", cfg, "diff", f"{args.snapshot_id}..{args.snapshot_id_end}"]

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error getting diff: {stderr}"

    if not stdout.strip():
        return f"No differences between snapshots #{args.snapshot_id} and #{args.snapshot_id_end}"

    return f"Diff between #{args.snapshot_id} and #{args.snapshot_id_end}:\n{stdout}"


def handle_status(args: SnapperArgs) -> str:
    """Show status (changed files) between two snapshots."""
    if args.snapshot_id is None or args.snapshot_id_end is None:
        return "Error: Both snapshot_id and snapshot_id_end are required for status action"

    cfg = args.get_config()
    cmd = ["-c", cfg, "status", f"{args.snapshot_id}..{args.snapshot_id_end}"]

    success, stdout, stderr = run_snapper_command(cmd)

    if not success:
        return f"Error getting status: {stderr}"

    if not stdout.strip():
        return f"No changes between snapshots #{args.snapshot_id} and #{args.snapshot_id_end}"

    return f"Changed files between #{args.snapshot_id} and #{args.snapshot_id_end}:\n{stdout}"


def handle_configs(args: SnapperArgs) -> str:
    """List available snapper configs."""
    success, stdout, stderr = run_snapper_command(["list-configs"], use_json=True)

    if not success:
        return f"Error listing configs: {stderr}"

    try:
        data = json.loads(stdout)
        # JSON output is wrapped: {"configs": [...]}
        configs_list = data.get("configs", [])
        if not configs_list:
            return "No snapper configurations found"

        lines = ["Available Snapper configurations:", ""]
        for cfg in configs_list:
            name = cfg.get("config", "unknown")
            subvol = cfg.get("subvolume", "unknown")
            default_marker = " (default)" if name == config.default_config else ""
            lines.append(f"  {name}: {subvol}{default_marker}")

        return "\n".join(lines)
    except json.JSONDecodeError:
        return f"Available configurations:\n{stdout}"


# Action handlers map for Snapper
SNAPPER_ACTION_HANDLERS = {
    SnapperAction.LIST: handle_list,
    SnapperAction.CREATE: handle_create,
    SnapperAction.DELETE: handle_delete,
    SnapperAction.ROLLBACK: handle_rollback,
    SnapperAction.CLEANUP: handle_cleanup,
    SnapperAction.DIFF: handle_diff,
    SnapperAction.STATUS: handle_status,
    SnapperAction.CONFIGS: handle_configs,
}


# =============================================================================
# BTRFS Health Tool
# =============================================================================

class BtrfsAction(str, Enum):
    """Available btrfs health actions."""
    USAGE = "usage"
    DEVICES = "devices"
    STATS = "stats"
    SCRUB_STATUS = "scrub_status"
    BALANCE_STATUS = "balance_status"
    DF = "df"
    FILESYSTEM_SHOW = "filesystem_show"


class BtrfsArgs(BaseModel):
    """Arguments for the btrfs_health tool."""
    action: BtrfsAction = Field(
        description="The btrfs action: usage (space usage), devices (list devices), stats (error statistics), scrub_status (scrub progress), balance_status (balance progress), df (data/metadata usage), filesystem_show (filesystem info)"
    )
    mount_point: Optional[str] = Field(
        default=None,
        description="BTRFS mount point (e.g., '/', '/home'). Uses default from SNAPPER_MCP_DEFAULT_MOUNT if not specified."
    )
    device: Optional[str] = Field(
        default=None,
        description="Specific device path for stats action (e.g., '/dev/sda1'). If not specified, uses mount point."
    )

    def get_mount_point(self) -> str:
        """Get the mount point, falling back to default."""
        return self.mount_point or config.default_mount


def run_btrfs_command(args: list[str]) -> tuple[bool, str, str]:
    """
    Execute a btrfs command, optionally with sudo.

    Returns: (success, stdout, stderr)
    """
    cmd = []

    if config.use_sudo:
        cmd.append(config.sudo_path)

    cmd.append(config.btrfs_path)
    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {config.timeout} seconds"
    except FileNotFoundError as e:
        return False, "", f"Command not found: {e.filename}. Check SNAPPER_MCP_BTRFS_PATH or SNAPPER_MCP_SUDO_PATH."
    except Exception as e:
        return False, "", str(e)


def handle_btrfs_usage(args: BtrfsArgs) -> str:
    """Show BTRFS filesystem usage."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["filesystem", "usage", mount])

    if not success:
        return f"Error getting filesystem usage: {stderr}"

    return f"BTRFS Filesystem Usage for {mount}:\n\n{stdout}"


def handle_btrfs_devices(args: BtrfsArgs) -> str:
    """List devices in the BTRFS filesystem."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["device", "stats", mount])

    if not success:
        # Try alternative command
        success, stdout, stderr = run_btrfs_command(["filesystem", "show", mount])
        if not success:
            return f"Error listing devices: {stderr}"

    return f"BTRFS Devices for {mount}:\n\n{stdout}"


def handle_btrfs_stats(args: BtrfsArgs) -> str:
    """Show device error statistics."""
    target = args.device or args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["device", "stats", target])

    if not success:
        return f"Error getting device stats: {stderr}"

    # Parse and summarize stats
    lines = stdout.strip().split('\n')
    has_errors = False
    for line in lines:
        if any(err in line for err in ['write_io_errs', 'read_io_errs', 'flush_io_errs', 'corruption_errs', 'generation_errs']):
            if not line.strip().endswith(' 0'):
                has_errors = True
                break

    status = "ERRORS DETECTED" if has_errors else "No errors detected"
    return f"BTRFS Device Statistics ({status}):\n\n{stdout}"


def handle_btrfs_scrub_status(args: BtrfsArgs) -> str:
    """Show scrub status."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["scrub", "status", mount])

    if not success:
        return f"Error getting scrub status: {stderr}"

    return f"BTRFS Scrub Status for {mount}:\n\n{stdout}"


def handle_btrfs_balance_status(args: BtrfsArgs) -> str:
    """Show balance status."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["balance", "status", mount])

    if not success:
        # "not in progress" is reported as error, but it's actually informative
        if "not in progress" in stderr.lower() or "not in progress" in stdout.lower():
            return f"BTRFS Balance Status for {mount}:\n\nNo balance operation in progress."
        return f"Error getting balance status: {stderr}"

    return f"BTRFS Balance Status for {mount}:\n\n{stdout}"


def handle_btrfs_df(args: BtrfsArgs) -> str:
    """Show data/metadata/system usage breakdown."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["filesystem", "df", mount])

    if not success:
        return f"Error getting filesystem df: {stderr}"

    return f"BTRFS Space Allocation for {mount}:\n\n{stdout}"


def handle_btrfs_filesystem_show(args: BtrfsArgs) -> str:
    """Show filesystem information."""
    mount = args.get_mount_point()
    success, stdout, stderr = run_btrfs_command(["filesystem", "show", mount])

    if not success:
        return f"Error getting filesystem info: {stderr}"

    return f"BTRFS Filesystem Info:\n\n{stdout}"


# Action handlers map for BTRFS
BTRFS_ACTION_HANDLERS = {
    BtrfsAction.USAGE: handle_btrfs_usage,
    BtrfsAction.DEVICES: handle_btrfs_devices,
    BtrfsAction.STATS: handle_btrfs_stats,
    BtrfsAction.SCRUB_STATUS: handle_btrfs_scrub_status,
    BtrfsAction.BALANCE_STATUS: handle_btrfs_balance_status,
    BtrfsAction.DF: handle_btrfs_df,
    BtrfsAction.FILESYSTEM_SHOW: handle_btrfs_filesystem_show,
}


# Create the MCP server
app = Server("btrfs-snapper-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the snapper and btrfs_health tools."""
    return [
        Tool(
            name="snapper",
            description=f"""Manage BTRFS snapshots via Snapper. A unified tool for all snapshot operations.

Actions:
- configs: List available snapper configurations
- list: Show all snapshots for a config
- create: Create a new snapshot (optionally with description)
- delete: Remove a snapshot by number
- rollback: Restore system to a previous snapshot (requires reboot)
- cleanup: Prune snapshots using an algorithm (number, timeline, empty-pre-post)
- diff: Show file differences between two snapshots
- status: List changed files between two snapshots

Current default config: {config.default_config}
Using sudo: {config.use_sudo}

Examples:
- List configs: action="configs"
- List snapshots: action="list", config="root"
- Create snapshot: action="create", config="root", description="Before update"
- Delete snapshot: action="delete", config="root", snapshot_id=5
- Compare snapshots: action="diff", config="root", snapshot_id=1, snapshot_id_end=5
- Cleanup old snapshots: action="cleanup", config="root", cleanup_algorithm="number"
""",
            inputSchema=SnapperArgs.model_json_schema()
        ),
        Tool(
            name="btrfs_health",
            description=f"""Check BTRFS filesystem health and status. Monitor disk usage, errors, and maintenance operations.

Actions:
- usage: Comprehensive filesystem space usage
- devices: List devices in the BTRFS array
- stats: Device error statistics (corruption, read/write errors)
- scrub_status: Status of scrub operation (data integrity check)
- balance_status: Status of balance operation (data redistribution)
- df: Space allocation by data type (Data, Metadata, System)
- filesystem_show: Filesystem information and device list

Current default mount: {config.default_mount}
Using sudo: {config.use_sudo}

Examples:
- Check usage: action="usage", mount_point="/"
- Check for errors: action="stats", mount_point="/"
- Scrub status: action="scrub_status", mount_point="/"
- Show filesystem: action="filesystem_show"
""",
            inputSchema=BtrfsArgs.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "snapper":
        try:
            args = SnapperArgs(**arguments)
        except Exception as e:
            return [TextContent(type="text", text=f"Invalid arguments: {e}")]

        handler = SNAPPER_ACTION_HANDLERS.get(args.action)
        if not handler:
            return [TextContent(type="text", text=f"Unknown action: {args.action}")]

        result = handler(args)
        return [TextContent(type="text", text=result)]

    elif name == "btrfs_health":
        try:
            args = BtrfsArgs(**arguments)
        except Exception as e:
            return [TextContent(type="text", text=f"Invalid arguments: {e}")]

        handler = BTRFS_ACTION_HANDLERS.get(args.action)
        if not handler:
            return [TextContent(type="text", text=f"Unknown action: {args.action}")]

        result = handler(args)
        return [TextContent(type="text", text=result)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Entry point for the CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
