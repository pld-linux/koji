# TODO
# - package real webapp
# - need pld packages:
#   python-krbV
# - add kojibuilder to mock group
Summary:	Build system tools
Summary(pl.UTF-8):	Narzędzia systemu budującego
Name:		koji
Version:	1.9.0
Release:	0.1
# koji.ssl libs (from plague) are GPLv2+
License:	LGPL v2 and GPL v2+
Group:		Applications/System
Source0:	https://fedorahosted.org/releases/k/o/koji/%{name}-%{version}.tar.bz2
# Source0-md5:	0ce900022f67324858551622f9f75c73
URL:		http://fedorahosted.org/koji
BuildRequires:	python
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
#Requires:	python-krbV >= 1.0.13
Requires:	python-pyOpenSSL
Requires:	python-rpm
Requires:	python-urlgrabber
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# TODO: change to libdir
%define		_libexecdir	%{_prefix}/libexec

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
# rpmdiff lib (from rpmlint) is GPLv2 (only)
License:	LGPL v2 and GPL v2
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_alias
Requires:	apache-mod_python
Requires:	python-PyGreSQL
Requires:	webapps

%description hub
koji-hub is the XMLRPC interface to the Koji database.

%description hub -l pl.UTF-8
koji-hub to interfejs XMLRPC do bazy danych Koji.

%package hub-plugins
Summary:	Koji hub plugins
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-hub = %{version}-%{release}

%description hub-plugins
Plugins to the koji XMLRPC interface

%package builder
Summary:	Koji RPM builder daemon
Summary(pl.UTF-8):	Demon systemu Koji budujący pakiety RPM
# mergerepos (from createrepo) is GPLv2+
License:	LGPL v2 and GPL v2+
Group:		Applications/System
Requires(post):	/sbin/chkconfig
Requires(pre):	/usr/sbin/useradd
Requires(preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	/usr/bin/cvs
Requires:	/usr/bin/git
Requires:	/usr/bin/svn
Requires:	createrepo >= 0.9.6
Requires:	mock >= 0.9.14
Requires:	pycdio
Requires:	python-cheetah
Requires:	python-pykickstart
Requires:	rpm-build

%description builder
koji-builder is the daemon that runs on build machines and executes
tasks that come through the Koji system.

%description builder -l pl.UTF-8
koji-builder to demon działający na maszynach budujących i wykonujący
zadania przychodzące poprzez system Koji.

%package vm
Summary:	Koji virtual machine management daemon
License:	LGPL v2
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires(post):	/sbin/chkconfig
Requires(post):	/sbin/service
Requires(preun):	/sbin/chkconfig
Requires(preun):	/sbin/service
Requires:	/usr/bin/virt-clone
Requires:	libvirt-python
Requires:	libxml2-python
Requires:	qemu-img

%description vm
koji-vm contains a supplemental build daemon that executes certain
tasks in a virtual machine.

This package is not required for most installations.

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
Requires:	apache-mod_wsgi
Requires:	python-PyGreSQL
Requires:	python-cheetah
#Requires:	python-krbV >= 1.0.13
Requires:	webapps

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

install -d $RPM_BUILD_ROOT%{py_sitescriptdir}
mv $RPM_BUILD_ROOT{%{_prefix}/lib/python2.7/site-packages/koji,%{py_sitescriptdir}/%{name}}

%clean
rm -rf $RPM_BUILD_ROOT

%pre builder
%useradd -u 221 -r -d /home/services/koji -s /bin/sh -c "Koji builder" -g nobody kojibuilder

%post builder
/sbin/chkconfig --add kojid
%service kojid restart

%preun builder
if [ "$1" = "0" ]; then
	%service kojid stop
	/sbin/chkconfig --del kojid
fi

%post vm
/sbin/chkconfig --add kojivmd

%preun vm
if [ $1 = 0 ]; then
	/sbin/chkconfig --del kojivmd
	%service kojivmd stop
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
%{py_sitescriptdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji.conf

%files hub
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd/webapps.d/kojihub.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji-hub/hub.conf
%{_datadir}/koji-hub
%dir %{_libexecdir}/koji-hub
%attr(755,root,root) %{_libexecdir}/koji-hub/rpmdiff

%files hub-plugins
%defattr(644,root,root,755)
%dir %{_sysconfdir}/koji-hub/plugins
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji-hub/plugins/messagebus.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji-hub/plugins/rpm2maven.conf
%dir %{_prefix}/lib/koji-hub-plugins
%{_prefix}/lib/koji-hub-plugins/*.py*

%files vm
%defattr(644,root,root,755)
%dir %{_sysconfdir}/kojivmd
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kojivmd/kojivmd.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojivmd
%attr(755,root,root) %{_sbindir}/kojivmd
%{_datadir}/kojivmd
%attr(754,root,root) /etc/rc.d/init.d/kojivmd

%files utils
%defattr(644,root,root,755)
%dir %{_sysconfdir}/kojira
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kojira/kojira.conf
%dir %{_sysconfdir}/koji-gc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji-gc/koji-gc.conf
%dir %{_sysconfdir}/koji-shadow
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/koji-shadow/koji-shadow.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojira
%attr(754,root,root) /etc/rc.d/init.d/kojira
%attr(755,root,root) %{_sbindir}/koji-gc
%attr(755,root,root) %{_sbindir}/kojira
%attr(755,root,root) %{_sbindir}/koji-shadow

%files web
%defattr(644,root,root,755)
%{_datadir}/koji-web
%dir %{_sysconfdir}/kojiweb
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kojiweb/web.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd/webapps.d/kojiweb.conf

%files builder
%defattr(644,root,root,755)
%dir %{_sysconfdir}/kojid
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/kojid/kojid.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kojid
%attr(754,root,root) /etc/rc.d/init.d/kojid
%attr(755,root,root) %{_sbindir}/kojid
%dir %{_libexecdir}/kojid
%attr(755,root,root) %{_libexecdir}/kojid/mergerepos
# TODO: kill -
%attr(-,kojibuilder,kojibuilder) %{_sysconfdir}/mock/koji
