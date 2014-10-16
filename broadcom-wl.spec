%define oname	hybrid-portsrc
%define kname	wl

Summary:	Proprietary driver for Broadcom wireless adapters
Name:		broadcom-wl
Version:	5.100.82.112
Release:	3
Source0:	http://www.broadcom.com/docs/linux_sta/%{oname}_x86_32-v5_100_82_112.tar.gz
Source1:	http://www.broadcom.com/docs/linux_sta/%{oname}_x86_64-v5_100_82_112.tar.gz
Source2:	blacklist-brcm80211.conf
Patch0:		broadcom-sta-5.100.82.111-linux-3.0.patch
Patch1:		broadcom-sta-5.100.82.112-linux-3.2.patch
Patch2:		broadcom-sta-5.100.82.112-linux-2.6.39.patch
# Blob is under a custom license (see LICENSE.txt), everything else
# is GPLv2 - AdamW 2008/12
License:	Freeware and GPLv2 with exception
Group:		System/Kernel and hardware
URL:		http://www.broadcom.com/support/802.11/linux_sta.php

%description
This package contains the proprietary driver for Broadcom wireless
adapters provided by Broadcom. If installed, it will be used for
these cards in preference to the third-party open source driver that
requires manual installation of firmware, or ndiswrapper.

%package -n dkms-%{name}
Summary:	Kernel module for Broadcom wireless adapters
Group:		System/Kernel and hardware
Requires(post):		dkms
Requires(preun):	dkms

%description -n dkms-%{name}
This package contains the proprietary driver for Broadcom wireless
adapters provided by Broadcom. If installed, it will be used for
these cards in preference to the third-party open source driver that
requires manual installation of firmware, or ndiswrapper.

%prep
%ifarch x86_64
%setup -q -T -c -a1 %{oname}
%else
%setup -q -T -c -a0 %{oname}
%endif
%patch0 -p1
%patch1 -p1
%patch2 -p0

%build

%install
# add blacklist for in-kernel module
install -m755 -d %{buildroot}/etc/modprobe.d/
install -m644 %{SOURCE2} %{buildroot}/etc/modprobe.d

# install dkms sources
mkdir -p %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}
cp -R * %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/
cat > %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/dkms.conf << EOF
MAKE="make -C \$kernel_source_dir M=\\\$(pwd)"
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}-%{release}
DEST_MODULE_LOCATION=/kernel/3rdparty/%{name}
BUILT_MODULE_NAME=%{kname}
AUTOINSTALL=yes
EOF

%post -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{name} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{name} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{name} -v %{version}-%{release}

%preun -n dkms-%{name}
# rmmod can fail
/sbin/rmmod %{kname} >/dev/null 2>&1
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{name} -v %{version}-%{release} --all || :

%files -n dkms-%{name}
%doc lib/LICENSE.txt
%config(noreplace) /etc/modprobe.d/blacklist-brcm80211.conf
%dir %{_usr}/src/%{name}-%{version}-%{release}
%{_usr}/src/%{name}-%{version}-%{release}/*
