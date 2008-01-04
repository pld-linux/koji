Summary:	Build system tools
Name:		koji
Version:	1.2.3
Release:	0.1
License:	LGPL
Group:		Applications/System
Source0:	%{name}-%{version}.tar.bz2
# Source0-md5:	22cc3917703906b92d009190101ca6d5
URL:		http://hosted.fedoraproject.org/projects/koji
BuildRequires:	python
Requires:	pyOpenSSL
Requires:	python-krbV >= 1.0.13
Requires:	python-rpm
Requires:	python-urlgrabber
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Koji is a system for building and tracking RPMS. The base package
contains shared libraries and the command-line interface.

%package hub
Summary:	Koji XMLRPC interface
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_python
Requires:	httpd
Requires:	python-postgresql

%description hub
koji-hub is the XMLRPC interface to the koji database

%package builder
Summary:	Koji RPM builder daemon
Group:		Applications/System
Requires(post):	/sbin/chkconfig
Requires(post):	/sbin/service
Requires(pre):	/usr/sbin/useradd
Requires(preun):	/sbin/chkconfig
Requires(preun):	/sbin/service
Requires:	%{name} = %{version}-%{release}
Requires:	/usr/bin/cvs
Requires:	/usr/bin/git
Requires:	/usr/bin/svn
Requires:	createrepo >= 0.4.11
Requires:	mock >= 0.8.7
Requires:	rpm-build

%description builder
koji-builder is the daemon that runs on build machines and executes
tasks that come through the Koji system.

%package utils
Summary:	Koji Utilities
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	python-postgresql

%description utils
Utilities for the Koji system

%package web
Summary:	Koji Web UI
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_auth_kerb
Requires:	apache-mod_python
Requires:	httpd
Requires:	python-cheetah
Requires:	python-krbV >= 1.0.13
Requires:	python-postgresql

%description web
koji-web is a web UI to the Koji system.

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%{py_sitedir}/%{name}
%config(noreplace) %{_sysconfdir}/koji.conf
%doc docs Authors COPYING LGPL

%files hub
%defattr(644,root,root,755)
%{_datadir}/koji-hub
%config(noreplace) %{_sysconfdir}/httpd/conf.d/kojihub.conf

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/kojira
%{_initrddir}/kojira
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojira
%{_sysconfdir}/kojira
%config(noreplace) %{_sysconfdir}/kojira/kojira.conf

%files web
%defattr(644,root,root,755)
%{_datadir}/koji-web
%{_sysconfdir}/kojiweb
%config(noreplace) %{_sysconfdir}/httpd/conf.d/kojiweb.conf

%files builder
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/kojid
%{_initrddir}/kojid
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojid
%{_sysconfdir}/kojid
%config(noreplace) %{_sysconfdir}/kojid/kojid.conf
%attr(-,kojibuilder,kojibuilder) %{_sysconfdir}/mock/koji

%pre builder
%useradd -r -s /bin/bash -G mock -d /builddir -M kojibuilder 2>/dev/null ||:

%post builder
/sbin/chkconfig --add kojid
/sbin/service kojid condrestart &> /dev/null || :

%preun builder
if [ $1 = 0 ]; then
  %service kojid stop &> /dev/null
  /sbin/chkconfig --del kojid
fi

%post utils
/sbin/chkconfig --add kojira
/sbin/service kojira condrestart &> /dev/null || :
%preun utils
if [ $1 = 0 ]; then
  %service kojira stop &> /dev/null || :
  /sbin/chkconfig --del kojira
fi
