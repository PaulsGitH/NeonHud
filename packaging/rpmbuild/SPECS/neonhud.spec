Name:           neonhud
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linux-native performance HUD (TUI) with systemd/RPM focus
License:        MIT
URL:            https://github.com/<your-username>/NeonHud
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3
Requires:       python3-psutil
Requires:       python3-rich

%description
NeonHud is a terminal UI for Linux system metrics with systemd integration.

%prep
%setup -q

%build
# Pure Python; no build step required

%install
# Placeholder: install files into %{buildroot}
# You will replace this with proper install paths in Issue 8.

%files
# Placeholder file list

%changelog
* Mon Aug 25 2025 You <you@example.com> - 0.1.0-1
- Initial RPM spec stub
