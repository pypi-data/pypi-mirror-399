# PORTWATCH

A tactical port scanner dashboard for developers. See what's running on your machine at a glance.

```
╔═══════════════════════════════════════╗
║  ▓▓▓ P O R T W A T C H ▓▓▓  v0.1.0    ║
╚═══════════════════════════════════════╝
```

## Installation

```bash
cd portwatch
pip install -e .
```

Or run directly:

```bash
pip install textual psutil rich
python -m portwatch
```

## Usage

```bash
portwatch
```

## Keybindings

| Key | Action |
|-----|--------|
| `↑↓` | Navigate ports |
| `Enter` | Open action menu |
| `b` | Open in browser |
| `k` | Kill process |
| `c` | Copy port |
| `r` | Manual refresh |
| `1/2/5` | Set refresh rate |
| `q` | Quit |

## Features

- Live auto-refresh (configurable 1s/2s/5s)
- Category grouping (Web, Database, Queue, DevTools, System)
- Process details (PID, memory, uptime, cmdline)
- Quick actions (browser, kill, copy)
- Docker container detection
- Tactical military aesthetic

## Requirements

- Python 3.10+
- macOS / Linux (Windows partial support)
