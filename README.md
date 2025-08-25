# NeonHud

NeonHud is a Linux-native performance HUD (terminal UI) focused on **system metrics, systemd integration, and RPM packaging**. It is open-source under the MIT License.

## Core goals
- Live TUI panels: CPU, Memory, Disk I/O, Network I/O
- Process table: PID, CMD, CPU%, RSS with sort & filter
- CLI tools: `neonhud report` (JSON snapshot), `neonhud profile` (kernel/distro/SELinux)
- System integration: collector runs as a systemd service (journald logs)
- Packaging: minimal RPM builds & installs cleanly on Fedora/RHEL
- Differentiator: **cgroup awareness** (Docker/Podman/systemd slices via `/proc/<pid>/cgroup`)

## Why terminal-native?
Fast to start, low overhead, and works over SSH. NeonHud emphasizes Linux fundamentals (procfs, systemd, cgroups) instead of browser dashboards.

## License
MIT — see [LICENSE](LICENSE).
