# NeonHud

NeonHud is a **Linux-native performance HUD** with a cyberpunk terminal aesthetic.  
It displays real-time system metrics (CPU, Memory, Disk I/O, Network, Processes) using a sleek Rich-based TUI.

- Language: **Python 3.11+**
- UI: **Rich** (tables, panels, live updates), themeable (cyberpunk preset)
- Packaging: **PEP 517/518** via `pyproject.toml`
- Quality: `pytest`, `mypy`, `ruff`, `black`
- Containers: **Docker** + `docker-compose`, **VS Code Dev Container**
- License: **MIT**

---

## ✨ Features

- **CPU**: total % + per-core  
- **Memory**: % + used/total  
- **Disk I/O**: read/write throughput (planned wiring in upcoming issues)  
- **Network I/O**: rx/tx throughput (planned wiring in upcoming issues)  
- **Processes**: top-N by CPU (normalized), RSS, command line  
- **Themes**: `classic`, `cyberpunk` (magenta/cyan/yellow on black)  
- **CLI**:
  - `neonhud report` → JSON snapshot
  - `neonhud top` → live process table
  - `neonhud dash` → live dashboard panels (CPU/Memory now; Disk/Net coming)

---

## 📦 Install (Local Dev)

> On Windows PowerShell:

~~~powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
~~~

On Linux/macOS:

~~~bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
~~~

### 🔧 Development Workflow

Run formatting, linting, types, and tests locally:

~~~bash
ruff check src tests --fix
black src tests
mypy -p neonhud
pytest -q
~~~

Editable install makes the CLI available:

~~~bash
neonhud --help
~~~

If the shell can’t find it, run via module:

~~~bash
python -m neonhud.cli --help
~~~

---

## 🖥️ CLI Usage

Pretty JSON report:

~~~bash
neonhud report --pretty
~~~

Live process table (configurable):

~~~bash
neonhud top --interval 1.0 --limit 20 --theme cyberpunk
~~~

Live dashboard (CPU + Memory now; Disk/Net soon):

~~~bash
neonhud dash --interval 1.0 --theme cyberpunk
~~~

### Config precedence

1. Env var `NEONHUD_CONFIG` → path to TOML file  
2. OS defaults:  
   - Windows → `%APPDATA%\NeonHud\config.toml`  
   - Linux/macOS → `~/.config/neonhud/config.toml`  
3. Built-in defaults (`theme=classic`, `refresh_interval=2.0`, `process_limit=15`)

### Logging

- Env var `NEONHUD_LOG_LEVEL` or config key `log_level` (e.g., `DEBUG`, `INFO`)  
- Logs go to **stderr**; JSON output stays on **stdout**

---

## 🐳 Running with Docker

Ensure Docker Desktop is installed and running. On Windows, prefer WSL 2 backend.

### Build and run manually

~~~bash
docker build -t neonhud:dev .
docker run --rm -it neonhud:dev --help
docker run --rm -it neonhud:dev dash --theme cyberpunk --interval 1
~~~

### Or with docker-compose

~~~bash
docker compose build
docker compose run --rm neonhud top --limit 15
docker compose run --rm neonhud dash --theme cyberpunk
~~~

**Notes**  
- Image includes editable install for quick iteration.  
- `docker-compose.yml` mounts your repo into `/app` and caches pip.  
- Default container command is `--help`; override with CLI args as needed.

---

## 🧪 Tests & Quality Gates

~~~bash
pytest -q               # tests
mypy -p neonhud         # type checking
ruff check src tests    # linting
black src tests         # formatting
~~~

CI can run these same commands to validate PRs.

---

## 🗂️ Project Structure

~~~text
NeonHud/
├─ src/
│  └─ neonhud/
│     ├─ core/          # config + logging
│     ├─ collectors/    # cpu, mem, procs (disk/net upcoming)
│     ├─ ui/            # themes, tables, panels, dashboard
│     ├─ utils/         # formatters, bars, time helpers
│     └─ cli.py         # CLI entry (report, top, dash)
├─ tests/               # pytest suite
├─ docker/
│  └─ entrypoint.sh     # forwards args to CLI
├─ .devcontainer/
│  └─ devcontainer.json # VS Code development container
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
├─ README.md
└─ LICENSE
~~~

---

## 🛠️ Troubleshooting

- `neonhud` not found → use `python -m neonhud.cli`, or re-activate venv.  
- Logs intermix with JSON → by design logs go to **stderr**; capture **stdout** for JSON.  
- `permission denied` in Docker → ensure `docker/entrypoint.sh` uses **LF** line endings; rebuild.  
- PowerShell script execution blocked → set a user-level policy once:

~~~powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
~~~

- Docker CLI not found → open a new shell; ensure PATH includes  
  `C:\Program Files\Docker\Docker\resources\bin`.

---

## 📍 Roadmap
 
- Full-screen Rich layout (gtop-style dashboard)  
- VS Code tasks for lint/test  
- Packaging: wheels + optional RPM spec for Fedora/RHEL demo

---

## 📜 License

MIT — see **LICENSE** for details.
