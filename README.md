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
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
On Linux/macOS:

bash
Copy code
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
🔧 Development Workflow
Run formatting, linting, types, and tests locally:

bash
Copy code
ruff check src tests --fix
black src tests
mypy -p neonhud
pytest -q
Editable install makes the CLI available:

bash
Copy code
neonhud --help
If the shell can’t find it, run via module:

bash
Copy code
python -m neonhud.cli --help

##🖥️ CLI Usage

Pretty JSON report:

bash
Copy code
neonhud report --pretty
Live process table (configurable):

bash
Copy code
neonhud top --interval 1.0 --limit 20 --theme cyberpunk
Live dashboard (CPU + Memory now; Disk/Net soon):

bash
Copy code
neonhud dash --interval 1.0 --theme cyberpunk
Config precedence:

Env var NEONHUD_CONFIG → path to TOML file

OS defaults (%APPDATA%\NeonHud\config.toml on Windows, ~/.config/neonhud/config.toml on Linux/macOS)

Built-in defaults (theme=classic, refresh_interval=2.0, process_limit=15)

Logging:

Env var NEONHUD_LOG_LEVEL or config key log_level (e.g., DEBUG, INFO)

Logs go to stderr; JSON output stays on stdout

##🐳 Running with Docker

Ensure Docker Desktop is installed and running. On Windows, prefer WSL 2 backend.

Build and run manually
bash
Copy code
docker build -t neonhud:dev .
docker run --rm -it neonhud:dev --help
docker run --rm -it neonhud:dev dash --theme cyberpunk --interval 1
Or with docker-compose
bash
Copy code
docker compose build
docker compose run --rm neonhud top --limit 15
docker compose run --rm neonhud dash --theme cyberpunk
Notes:

Image includes editable install for quick iteration.

docker-compose.yml mounts your repo into /app and caches pip.

Default container command is --help; override with CLI args as needed.

##🧪 Tests & Quality Gates

Tests: pytest -q

Type checking: mypy -p neonhud

Linting: ruff check src tests --fix

Formatting: black src tests

CI can run these same commands to validate PRs.

##🗂️ Project Structure

bash
Copy code
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

##🛠️ Troubleshooting

neonhud not found in shell: use python -m neonhud.cli, or re-activate venv.

Logs intermix with JSON: by design logs go to stderr; capture stdout for JSON.

Docker permission denied on entrypoint: ensure docker/entrypoint.sh uses LF line endings; rebuild image.

Windows PowerShell script execution blocked: set a user-level policy once:

powershell
Copy code
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Docker CLI not found: open new shell after install; ensure PATH contains
C:\Program Files\Docker\Docker\resources\bin.

##📍 Roadmap

Add Disk/Network collectors + panels with sparklines

Full-screen Rich layout (gtop-style dashboard)

VS Code tasks for lint/test

Packaging: wheels + optional RPM spec for Fedora/RHEL demo


## License
MIT — see [LICENSE](LICENSE).
