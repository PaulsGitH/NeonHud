Name:           neonhud
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linux-native performance HUD with cyberpunk terminal aesthetic

License:        MIT
URL:            https://github.com/yourusername/NeonHud
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3-psutil
Requires:       python3-rich

%description
NeonHud is a Linux-native performance HUD (terminal UI) that displays
real-time CPU, memory, disk I/O, network, and process metrics with a
sleek cyberpunk theme. It integrates with systemd and can be installed
as an RPM package on Fedora/RHEL.

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{_bindir}/neonhud
%{python3_sitelib}/neonhud*

%changelog
* Tue Sep 01 2025 Your Name <you@example.com> - 0.1.0-1
- Initial RPM spec scaffolding for NeonHud
