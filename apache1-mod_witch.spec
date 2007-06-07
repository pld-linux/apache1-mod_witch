%define		mod_name	witch
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: log the access_log and error_log log into the syslogd
Summary(pl.UTF-8):	Moduł do apache przekazujący access_log i error_log do demona syslogd
Name:		apache1-mod_%{mod_name}
Version:	0.0.5
Release:	4
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://savannah.nongnu.org/download/mod-witch/mod-witch.pkg/%{version}/mod-witch-%{version}.tar.gz
# Source0-md5:	a2ffe2f9e28947426321615e2ba57fc7
Source1:	%{name}.conf
URL:		http://savannah.nongnu.org/projects/mod-witch/
BuildRequires:	apache1-apxs
BuildRequires:	apache1-devel >= 1.3.33-2
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(triggerpostun):	%{apxs}
Requires(triggerpostun):	grep
Requires(triggerpostun):	sed >= 4.0
Requires:	apache1(EAPI)
Obsoletes:	apache-mod_witch <= 0.0.5
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
This mod_witch apache module project intend to help the Apache web
server to log the access_log and error_log log into the syslogd, this
way apache will be able to log onto a remote logger machine with the
syslogd.

%description -l pl.UTF-8
Moduł apache'a mod_witch ma pomóc serwerowi WWW apache przekazywać
logi access_log i error_log do syslogd, umożliwiając w ten sposób
logowanie na inną maszynę.

%prep
%setup -q -n mod-%{mod_name}-%{version}

%build
%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.so

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/conf.d}

install mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q apache restart

%postun
if [ "$1" = "0" ]; then
	%service -q apache restart
fi

%triggerpostun -- %{name} < 0.0.5-2.1
if grep -q '^Include conf\.d/\*\.conf' /etc/apache/apache.conf; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	sed -i -e '
		/^Include.*mod_%{mod_name}\.conf/d
	' /etc/apache/apache.conf
else
	# they're still using old apache.conf
	sed -i -e '
		s,^Include.*mod_%{mod_name}\.conf,Include %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf,
	' /etc/apache/apache.conf
fi
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog README TODO
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*
