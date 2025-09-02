# NeonHud

NeonHud is a **Linux-native performance HUD** with a cyberpunk terminal aesthetic.  
It displays real-time system metrics (CPU, Memory, Disk I/O, Network, Processes) using a sleek **Rich-based TUI**.

- Language: **Python 3.11+**
- UI: **Rich** (tables, panels, sparklines, live updates), themeable (`classic`, `cyberpunk`)
- Packaging: **PEP 517/518** via `pyproject.toml`
- Quality: `pytest`, `mypy`, `ruff`, `black`
- Containers: **Docker** + `docker-compose`, **VS Code Dev Container**
- License: **MIT**

---

## ✨ Features

- **CPU**: total % + per-core usage, history sparkline  
- **Memory**: % + used/total, swap usage, history sparkline  
- **Disk I/O**: read/write throughput per device  
- **Network I/O**: rx/tx throughput per NIC, history sparkline  
- **Processes**: top-N by CPU, RSS, command line  
- **Themes**:  
  - `classic` → bold white + green on black  
  - `cyberpunk` → neon magenta, cyan, pink, and light red on black  
- **CLI Commands**:  
  - `neonhud report` → JSON snapshot  
  - `neonhud top` → live process table  
  - `neonhud dash` → dashboard panels (CPU + Memory)  
  - `neonhud pro` → full gtop-style system dashboard  

---

## 📦 Install (Local Dev)

### Windows PowerShell

~~~powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
~~~

### Linux/macOS

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

Live process table:

~~~bash
neonhud top --interval 1.0 --limit 20 --theme cyberpunk
~~~

Live dashboard (CPU + Memory panels):

~~~bash
neonhud dash --interval 1.0 --theme cyberpunk
~~~

Full gtop-style professional dashboard:

~~~bash
neonhud pro --interval 1.0 --theme cyberpunk
~~~

---

## ⚙️ Config Precedence

1) Env var `NEONHUD_CONFIG` → path to TOML file  
2) OS defaults:  
   - Windows → `%APPDATA%\NeonHud\config.toml`  
   - Linux/macOS → `~/.config/neonhud/config.toml`  
3) Built-in defaults (`theme=classic`, `refresh_interval=2.0`, `process_limit=15`)

---

## 📝 Logging

- Env var `NEONHUD_LOG_LEVEL` or config key `log_level` (`DEBUG`, `INFO`, etc.)  
- Logs go to **stderr**; JSON output stays on **stdout**

---

## 🐳 Running with Docker

Ensure Docker Desktop is installed and running. On Windows, prefer WSL 2 backend.

### Build and run manually

~~~bash
docker build -t neonhud:dev .
docker run --rm -it neonhud:dev --help
docker run --rm -it neonhud:dev pro --theme cyberpunk --interval 1
~~~

### Or with docker-compose

~~~bash
docker compose build
docker compose run --rm neonhud top --limit 15
docker compose run --rm neonhud pro --theme cyberpunk
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
│     ├─ collectors/    # cpu, mem, disk, net, procs
│     ├─ ui/            # themes, tables, panels, dashboards (classic + pro)
│     ├─ utils/         # formatters, bars, time helpers
│     └─ cli.py         # CLI entry (report, top, dash, pro)
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

- `neonhud not found` → use `python -m neonhud.cli`, or re-activate venv.  
- Logs intermix with JSON → logs go to **stderr**, capture **stdout** for JSON.  
- `permission denied` in Docker → ensure `docker/entrypoint.sh` uses **LF** line endings; rebuild.  
- PowerShell execution blocked → set policy once:

~~~powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
~~~

- Docker CLI not found → open a new shell; ensure PATH includes  
  `C:\Program Files\Docker\Docker\resources\bin`.

---

## 📜 License

MIT — see **LICENSE** for details.
