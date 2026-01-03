# BTRFS Snapper MCP

[![PyPI](https://img.shields.io/pypi/v/snapper-mcp)](https://pypi.org/project/snapper-mcp/)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet?logo=anthropic)](https://claude.ai/code)

An MCP (Model Context Protocol) server for managing BTRFS snapshots via [Snapper](http://snapper.io/) and monitoring BTRFS filesystem health. Exposes two unified tools with action-based dispatch to minimize tool proliferation while providing full snapshot management and disk health monitoring.

## Features

- **Two-tool design**: `snapper` for snapshots, `btrfs_health` for filesystem monitoring
- **Full Snapper support**: list, create, delete, rollback, cleanup, diff, status
- **BTRFS health monitoring**: usage, device stats, scrub status, balance status
- **Flexible configuration**: Environment variables for cross-system portability
- **No hardcoded paths**: Works with any Snapper configuration and mount points

## Installation

### From PyPI (recommended)

```bash
pip install snapper-mcp
```

### Using uvx (no install required)

```bash
uvx snapper-mcp
```

### From source

```bash
git clone https://github.com/danielrosehill/BTRFS-Snapper-MCP.git
cd BTRFS-Snapper-MCP
pip install -e .
```

## Configuration

The server is configured via environment variables, making it portable across systems:

| Variable | Default | Description |
|----------|---------|-------------|
| `SNAPPER_MCP_USE_SUDO` | `true` | Set to `false` if user has direct permissions |
| `SNAPPER_MCP_SNAPPER_PATH` | `snapper` | Path to snapper binary |
| `SNAPPER_MCP_BTRFS_PATH` | `btrfs` | Path to btrfs binary |
| `SNAPPER_MCP_SUDO_PATH` | `sudo` | Path to sudo binary |
| `SNAPPER_MCP_DEFAULT_CONFIG` | `root` | Default snapper config name |
| `SNAPPER_MCP_DEFAULT_MOUNT` | `/` | Default BTRFS mount point |
| `SNAPPER_MCP_TIMEOUT` | `60` | Command timeout in seconds |

## MCP Client Configuration

### Claude Code / Claude Desktop

Add to your MCP settings (e.g., `~/.claude/settings.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "btrfs-snapper": {
      "command": "uvx",
      "args": ["snapper-mcp"]
    }
  }
}
```

### With custom configuration

```json
{
  "mcpServers": {
    "btrfs-snapper": {
      "command": "uvx",
      "args": ["snapper-mcp"],
      "env": {
        "SNAPPER_MCP_DEFAULT_CONFIG": "root",
        "SNAPPER_MCP_DEFAULT_MOUNT": "/",
        "SNAPPER_MCP_USE_SUDO": "true"
      }
    }
  }
}
```

## Tools

### `snapper` - Snapshot Management

Manages BTRFS snapshots via Snapper.

#### Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `configs` | List available snapper configurations | - |
| `list` | Show all snapshots for a config | `config` (optional) |
| `create` | Create a new snapshot | `config`, `description` (optional) |
| `delete` | Remove a snapshot by number | `config`, `snapshot_id` |
| `rollback` | Restore to a previous snapshot | `config`, `snapshot_id` |
| `cleanup` | Prune snapshots using an algorithm | `config`, `cleanup_algorithm` |
| `diff` | Show file differences between snapshots | `config`, `snapshot_id`, `snapshot_id_end` |
| `status` | List changed files between snapshots | `config`, `snapshot_id`, `snapshot_id_end` |

#### Examples

```json
// List configurations
{"action": "configs"}

// List snapshots
{"action": "list", "config": "root"}

// Create snapshot
{"action": "create", "config": "root", "description": "Before system update"}

// Delete snapshot
{"action": "delete", "config": "root", "snapshot_id": 5}

// Rollback (requires reboot)
{"action": "rollback", "config": "root", "snapshot_id": 3}

// Cleanup with algorithm
{"action": "cleanup", "config": "root", "cleanup_algorithm": "number"}

// Compare snapshots
{"action": "diff", "config": "root", "snapshot_id": 1, "snapshot_id_end": 5}
```

Cleanup algorithms:
- `number`: Keep a fixed number of snapshots
- `timeline`: Keep snapshots based on age (hourly, daily, weekly, monthly, yearly)
- `empty-pre-post`: Remove empty pre/post snapshot pairs

### `btrfs_health` - Filesystem Health Monitoring

Monitors BTRFS filesystem health and status.

#### Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `usage` | Comprehensive filesystem space usage | `mount_point` (optional) |
| `devices` | List devices in the BTRFS array | `mount_point` (optional) |
| `stats` | Device error statistics | `mount_point`, `device` (optional) |
| `scrub_status` | Status of scrub operation | `mount_point` (optional) |
| `balance_status` | Status of balance operation | `mount_point` (optional) |
| `df` | Space allocation by data type | `mount_point` (optional) |
| `filesystem_show` | Filesystem information | `mount_point` (optional) |

#### Examples

```json
// Check filesystem usage
{"action": "usage", "mount_point": "/"}

// Check for device errors
{"action": "stats", "mount_point": "/"}

// Check scrub status
{"action": "scrub_status", "mount_point": "/"}

// Show data/metadata allocation
{"action": "df", "mount_point": "/"}

// Show filesystem info
{"action": "filesystem_show"}
```

## Prerequisites

- Linux with BTRFS filesystem
- [Snapper](http://snapper.io/) installed and configured (for snapshot management)
- Python 3.10+
- Sudo access (unless running as root or with appropriate permissions)

### Installing Snapper

**Ubuntu/Debian:**
```bash
sudo apt install snapper
```

**Fedora/openSUSE:**
```bash
sudo dnf install snapper
# or
sudo zypper install snapper
```

### Creating Snapper Configs

```bash
# For root filesystem
sudo snapper -c root create-config /

# For home partition
sudo snapper -c home create-config /home
```

## Sudo Configuration

For passwordless operation, add to `/etc/sudoers.d/btrfs-snapper`:

```
yourusername ALL=(ALL) NOPASSWD: /usr/bin/snapper
yourusername ALL=(ALL) NOPASSWD: /usr/bin/btrfs
```

Or disable sudo if you have direct permissions:

```json
{
  "env": {
    "SNAPPER_MCP_USE_SUDO": "false"
  }
}
```

## Adapting for Other Systems

### Different Snapshot Tools

The architecture can be adapted for other snapshot tools (e.g., Timeshift, ZFS snapshots) by:

1. Replacing the `run_snapper_command()` function with your tool's CLI
2. Adjusting the action handlers for your tool's command syntax
3. Updating environment variables as needed

### Different Filesystems

For ZFS or other filesystems:

1. Replace `run_btrfs_command()` with your filesystem's CLI
2. Update `BtrfsAction` enum with relevant actions
3. Implement new handlers for your filesystem's commands

The action-dispatch pattern remains the same regardless of underlying tools.

## License

MIT
