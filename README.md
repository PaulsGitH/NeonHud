# NeonHud

NeonHud is a Linux-native performance HUD (terminal UI) focused on **system metrics, systemd integration, and RPM packaging**.  
It is open-source under the MIT License.

## Core goals
- Live TUI panels: CPU, Memory, Disk I/O, Network I/O
- Process table: PID, CMD, CPU%, RSS with sort & filter
- CLI tools: `neonhud report` (JSON snapshot), `neonhud profile` (kernel/distro/SELinux)
- System integration: collector runs as a systemd service (journald logs)
- Packaging: minimal RPM builds & installs cleanly on Fedora/RHEL
- One differentiator: **cgroup awareness** *or* **SELinux posture/AVC explainer**

## Why terminal-native?
Terminal dashboards are **fast to start, low overhead, and work over SSH**.  
NeonHud emphasizes Linux fundamentals — procfs, systemd, SELinux — instead of browser dashboards.

## Roadmap (beyond MVP)
- GPU panel
- Replay/diff mode for performance traces
- Podmanized collector
- Devcontainer setup for contributors
- Cyberpunk aesthetic polish (themes, glow, glitch title)

## License
MIT — see [LICENSE](LICENSE).
