Summary:	Build system tools
Summary(pl.UTF-8):	Narzędzia systemu budującego
Name:		koji
Version:	1.2.3
Release:	0.1
License:	LGPL v2.1
Group:		Applications/System
Source0:	%{name}-%{version}.tar.bz2
# Source0-md5:	22cc3917703906b92d009190101ca6d5
URL:		http://hosted.fedoraproject.org/projects/koji
BuildRequires:	python
Requires:	python-krbV >= 1.0.13
Requires:	python-pyOpenSSL
Requires:	python-rpm
Requires:	python-urlgrabber
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Koji is a system for building and tracking RPMS. The base package
contains shared libraries and the command-line interface.

%description -l pl.UTF-8
Koji to system do budowania i śledzenia pakietów RPM. Podstawowy
pakiet zawiera biblioteki współdzielone i interfejs linii poleceń.

%package hub
Summary:	Koji XMLRPC interface
Summary(pl.UTF-8):	Interfejs XMLRPC do Koji
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_alias
Requires:	apache-mod_python
Requires:	webapps
Requires:	python-PyGreSQL

%description hub
koji-hub is the XMLRPC interface to the Koji database.

%description hub -l pl.UTF-8
koji-hub to interfejs XMLRPC do bazy danych Koji.

%package builder
Summary:	Koji RPM builder daemon
Summary(pl.UTF-8):	Demon systemu Koji budujący pakiety RPM
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

%description builder -l pl.UTF-8
koji-builder to demon działający na maszynach budujących i wykonujący
zadania przychodzące poprzez system Koji.

%package utils
Summary:	Koji Utilities
Summary(pl.UTF-8):	Narzędzia Koji
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	python-PyGreSQL

%description utils
Utilities for the Koji system.

%description utils -l pl.UTF-8
Narzędzia dla systemu Koji.

%package web
Summary:	Koji Web UI
Summary(pl.UTF-8):	Interfejs WWW do Koji
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_auth_kerb
Requires:	apache-mod_authz_host
Requires:	apache-mod_mime
Requires:	apache-mod_python
Requires:	webapps
Requires:	python-cheetah
Requires:	python-krbV >= 1.0.13
Requires:	python-PyGreSQL

%description web
koji-web is a Web UI to the Koji system.

%description web -l pl.UTF-8
koji-web to interfejs WWW do systemu Koji.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_sysconfdir}/httpd/{conf.d,webapps.d}

%clean
rm -rf $RPM_BUILD_ROOT

%pre builder
# TODO: don't use 55 (reserved for xdm)
%useradd -u 55 -r -d /home/services/koji -s /bin/false -c "Koji builder" -g nobody kojibuilder

%post builder
/sbin/chkconfig --add kojid
%service kojid restart

%preun builder
if [ "$1" = "0" ]; then
	%service kojid stop
	/sbin/chkconfig --del kojid
fi

%post utils
/sbin/chkconfig --add kojira
%service kojira restart

%preun utils
if [ "$1" = "0" ]; then
	%service kojira stop
	/sbin/chkconfig --del kojira
fi

%files
%defattr(644,root,root,755)
%doc docs Authors COPYING
%attr(755,root,root) %{_bindir}/*
%{py_sitedir}/%{name}
%config(noreplace) %{_sysconfdir}/koji.conf

%files hub
%defattr(644,root,root,755)
%{_datadir}/koji-hub
%config(noreplace) %{_sysconfdir}/httpd/webapps.d/kojihub.conf

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/kojira
%attr(754,root,root) /etc/rc.d/init.d/kojira
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojira
%{_sysconfdir}/kojira
%config(noreplace) %{_sysconfdir}/kojira/kojira.conf

%files web
%defattr(644,root,root,755)
%{_datadir}/koji-web
%{_sysconfdir}/kojiweb
%config(noreplace) %{_sysconfdir}/httpd/webapps.d/kojiweb.conf

%files builder
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/kojid
%attr(754,root,root) /etc/rc.d/init.d/kojid
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojid
%{_sysconfdir}/kojid
%config(noreplace) %{_sysconfdir}/kojid/kojid.conf
# TODO: kill -
%attr(-,kojibuilder,kojibuilder) %{_sysconfdir}/mock/koji
