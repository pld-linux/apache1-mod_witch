%define		mod_name	witch
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: log the access_log and error_log log into the syslogd
Summary(pl):	Modu³ do apache: loguje pliki access_log i error_log do demona syslogd
Name:		apache-mod_%{mod_name}
Version:	0.0.5
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://savannah.nongnu.org/download/mod-witch/mod-witch.pkg/%{version}/mod-witch-%{version}.tar.gz
# Source0-md5:	a2ffe2f9e28947426321615e2ba57fc7
Source1:	apache-mod_witch.conf
URL:		http://savannah.nongnu.org/projects/mod-witch
BuildRequires:	%{apxs}
BuildRequires:	apache(EAPI)-devel
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache(EAPI)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define         _sysconfdir     /etc/httpd

%description
This mod-witch apache module [1] project intend to help the Apache web
server [1] to log the access_log and error_log log into the syslogd
[2], this way apache will be able to log onto a remote logger machine
with the syslogd.

%description -l pl

%prep
%setup -q -n mod-%{mod_name}-%{version}

%build
%{apxs} -Wc,-Wall,-pipe -c mod_%{mod_name}.c -o mod_%{mod_name}.so

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}

install mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_%{mod_name}.conf" /etc/httpd/httpd.conf; then
        echo "Include /etc/httpd/mod_%{mod_name}.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	umask 027
	grep -v "^Include.*mod_%{mod_name}.conf" /etc/httpd/httpd.conf > \
                /etc/httpd/httpd.conf.tmp
        mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README INSTALL COPYING
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mod_*.conf
%attr(755,root,root) %{_pkglibdir}/*
