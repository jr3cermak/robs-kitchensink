%define MS_REL %{nil}

Name:           mapserver%{MS_REL}
Version:        6.2.1
Release:        6%{?dist}
Summary:        Environment for building spatially-enabled internet applications

Group:          Development/Tools
License:        BSD
URL:            http://www.mapserver.org

Source0:        http://download.osgeo.org/mapserver/mapserver-%{version}.tar.gz
%if 0%{MS_REL}
Patch0:         %{name}-%{version}-java-%{MS_REL}.patch
Patch1:         %{name}-%{version}-perl-%{MS_REL}.patch
Patch2:         %{name}-%{version}-python-%{MS_REL}.patch
%endif
# Fix check for libgd version (to be reported upstream)
Patch3:         %{name}-6.2.1-gdver.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       httpd
Requires:       dejavu-sans-fonts

BuildRequires:  libXpm-devel readline-devel
BuildRequires:  httpd-devel php-devel libxslt-devel pam-devel fcgi-devel
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  postgresql-devel mysql-devel java-devel
BuildRequires:  swig > 1.3.24 java
BuildRequires:  geos-devel proj-devel gdal-devel agg-devel cairo-devel
BuildRequires:  freetype-devel gd-devel >= 2.0.16
BuildRequires:  python-devel curl-devel zlib-devel libxml2-devel
BuildRequires:  libjpeg-devel libpng-devel libtiff-devel fribidi-devel giflib-devel


%define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")

%description
Mapserver is an internet mapping program that converts GIS data to
map images in real time. With appropriate interface pages, 
Mapserver can provide an interactive internet map based on 
custom GIS data.

%package -n php-%{name}
Summary:        PHP/Mapscript map making extensions to PHP
Group:          Development/Languages
BuildRequires:  php-devel
Requires:       php-gd%{?_isa}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

%description -n php-%{name}
The PHP/Mapscript extension provides full map customization capabilities within
the PHP scripting language.


%package perl
Summary:        Perl/Mapscript map making extensions to Perl
Group:          Development/Languages
Requires:       %{name} = %{version}-%{release}
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description perl
The Perl/Mapscript extension provides full map customization capabilities
within the Perl programming language.

%package python
Summary:        Python/Mapscript map making extensions to Python
Group:          Development/Languages
Requires:       %{name} = %{version}-%{release}

%description python
The Python/Mapscript extension provides full map customization capabilities
within the Python programming language.

%package java
Summary:        Java/Mapscript map making extensions to Java
Group:          Development/Languages
Requires:       %{name} = %{version}-%{release}
Requires:       java-gcj-compat 

%description java
The Java/Mapscript extension provides full map customization capabilities
within the Java programming language.

%prep
%setup -q -n mapserver-%{version}
%if 0%{MS_REL}
%patch0 -p1 -b .java
%patch1 -p1 -b .perl
%patch2 -p1 -b .python
%endif
%patch3 -p1 -b .gdver

# fix spurious perm bits
chmod -x mapscript/python/examples/*.py
chmod -x mapscript/python/tests/rundoctests.dist
chmod -x mapscript/perl/examples/*.pl


# replace fonts for tests with symlinks
rm -rf tests/vera/Vera.ttf
rm -rf tests/vera/VeraBd.ttf
pushd tests/vera/
ln -sf /usr/share/fonts/dejavu/DejaVuSans.ttf Vera.ttf
ln -sf /usr/share/fonts/dejavu/DejaVuSans-Bold.ttf VeraBd.ttf
popd

%build

CFLAGS="${CFLAGS} -ldl" ; export CFLAGS

# fix a UTF-8 one
iconv -f ISO-8859-1 -t UTF-8 < \
mapscript/java/examples/QueryByAttributeUnicode.java > \
mapscript/java/examples/QueryByAttributeUnicode-tmp.java
mv -f mapscript/java/examples/QueryByAttributeUnicode-tmp.java \
mapscript/java/examples/QueryByAttributeUnicode.java

# fix gdal lookup
%{__sed} -i.libs -e 's|`\$GDAL_CONFIG --dep-libs`||' configure

%configure \
   --with-gd \
   --with-zlib \
   --with-tiff \
   --with-agg \
   --with-experimental-png \
   --with-freetype=%{_bindir}/freetype-config \
   --with-gdal=%{_bindir}/gdal-config \
   --with-ogr=%{_bindir}/gdal-config \
   --with-geos=%{_bindir}/geos-config \
   --with-cairo=yes \
   --with-proj \
   --with-wfs \
   --with-wcs \
   --with-sos \
   --with-kml \
   --with-wmsclient \
   --with-wfsclient \
   --with-xpm \
   --with-postgis=%{_bindir}/pg_config \
   --with-mygis=%{_bindir}/mysql_config \
   --with-curl-config=%{_bindir}/curl-config \
   --with-xml2-config=%{_bindir}/xml2-config \
   --with-php=%{_bindir}/php-config \
   --with-fribidi-config=%{_libdir}/pkgconfig/fribidi.pc \
   --with-fastcgi=/usr \
   --without-pdf \
   --without-eppl \
   --with-threads \
   --enable-debug \
   --disable-runpath

# disable pgport library lookup.
for makefile in `find . -type f -name 'Makefile'`; do
sed -i 's|-lpgport||g' $makefile
done

# WARNING !!!
# using %{?_smp_mflags} may break build
make

# build perl
pushd mapscript/perl
%if 0%{MS_REL}
mv mapscript.pm mapscript%{MS_REL}.pm
%endif
perl Makefile.PL
make DESTDIR=%{buildroot} pure_vendor_install
popd

# build python
pushd mapscript/python
python setup.py build
popd

# build java
pushd mapscript/java
make JAVA_HOME=/etc/alternatives/java_sdk
popd

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}/%{_sysconfdir}/php.d
mkdir -p %{buildroot}%{_libdir}/php/modules
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
install -p -m 755 .libs/mapserv %{buildroot}%{_libexecdir}/mapserver%{MS_REL}
install -p -m 755 .libs/legend %{buildroot}/%{_bindir}/legend%{MS_REL}
install -p -m 755 .libs/msencrypt %{buildroot}/%{_bindir}/msencrypt%{MS_REL}
install -p -m 755 .libs/scalebar %{buildroot}/%{_bindir}/scalebar%{MS_REL}
install -p -m 755 .libs/shp2img %{buildroot}/%{_bindir}/shp2img%{MS_REL}
install -p -m 755 .libs/shptree %{buildroot}/%{_bindir}/shptree%{MS_REL}
install -p -m 755 .libs/shptreetst %{buildroot}/%{_bindir}/shptreetst%{MS_REL}
install -p -m 755 .libs/shptreevis %{buildroot}/%{_bindir}/shptreevis%{MS_REL}
install -p -m 755 .libs/sortshp %{buildroot}/%{_bindir}/sortshp%{MS_REL}
install -p -m 755 .libs/tile4ms %{buildroot}/%{_bindir}/tile4ms%{MS_REL}

install -p -m 755 .libs/libmapserver-%{version}.so %{buildroot}%{_libdir}/

install -p -m 644 xmlmapfile/mapfile.xsd %{buildroot}%{_datadir}/%{name}
install -p -m 644 xmlmapfile/mapfile.xsl %{buildroot}%{_datadir}/%{name}

install -p -m 755 mapscript/php/.libs/php_mapscript-%{version}.so %{buildroot}/%{_libdir}/php/modules/php_mapscript%{MS_REL}.so

# install perl module
pushd mapscript/perl
make DESTDIR=%{buildroot} pure_vendor_install
popd

# install python module
pushd mapscript/python
python setup.py install --root %{buildroot}
popd

# install java
mkdir -p %{buildroot}%{_javadir}
install -p -m 644 mapscript/java/mapscript%{MS_REL}.jar %{buildroot}%{_javadir}/
install -p -m 755 mapscript/java/.libs/libjavamapscript-%{version}.so %{buildroot}%{_libdir}/

# install php config file
mkdir -p %{buildroot}%{_sysconfdir}/php.d/
cat > %{buildroot}%{_sysconfdir}/php.d/%{name}.ini <<EOF
; Enable %{name} extension module
extension=php_mapscript%{MS_REL}.so
EOF

# cleanup junks
for junk in {*.pod,*.bs,.packlist} ; do
find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done

# fix some exec bits
chmod 755 %{buildroot}%{perl_vendorarch}/auto/mapscript%{MS_REL}/mapscript%{MS_REL}.so

%files
%defattr(-,root,root)
%doc README COMMITERS GD-COPYING HISTORY.TXT  
%doc INSTALL MIGRATION_GUIDE.txt
%doc symbols tests
%doc fonts
%{_bindir}/legend%{MS_REL}
%{_bindir}/msencrypt%{MS_REL}
%{_bindir}/scalebar%{MS_REL}
%{_bindir}/shp2img%{MS_REL}
%{_bindir}/shptree%{MS_REL}
%{_bindir}/shptreetst%{MS_REL}
%{_bindir}/shptreevis%{MS_REL}
%{_bindir}/sortshp%{MS_REL}
%{_bindir}/tile4ms%{MS_REL}
%{_libdir}/libmapserver-%{version}.so
%{_libexecdir}/%{name}
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*

%files -n php-%{name}
%defattr(-,root,root)
%doc mapscript/php/README
%doc mapscript/php/examples
%config(noreplace) %{_sysconfdir}/php.d/%{name}.ini
%{_libdir}/php/modules/php_mapscript%{MS_REL}.so

%files perl
%defattr(-,root,root)
%doc mapscript/perl/examples
%dir %{perl_vendorarch}/auto/mapscript%{MS_REL}
%{perl_vendorarch}/auto/mapscript%{MS_REL}/*
%{perl_vendorarch}/mapscript%{MS_REL}.pm

%files python
%defattr(-,root,root)
%doc mapscript/python/README
%doc mapscript/python/examples
%doc mapscript/python/tests
%{python_sitearch}/*

%files java
%defattr(-,root,root)
%doc mapscript/java/README
%doc mapscript/java/examples
%doc mapscript/java/tests
%{_javadir}/*.jar
%{_libdir}/libjavamapscript-%{version}.so

%changelog
* Mon May 19 2014 Rob Cermak <rob.cermak@gmail.com> - 6.2.1-6
- Add kml support
* Tue Aug 27 2013 Orion Poplawski <orion@cora.nwra.com> - 6.2.1-5
- Rebuild for gdal 1.10.0

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 6.2.1-3
- Perl 5.18 rebuild

* Tue Jun 11 2013 Remi Collet <rcollet@redhat.com> - 6.2.1-2
- rebuild for new GD 2.1.0

* Tue May 21 2013 Pavel Lisý <pali@fedoraproject.org> - 6.2.1-1
- Update to latest stable release
- BZ 910689 - dependency on bitstream-vera-sans-fonts changed to dejavu-sans-fonts
- BZ 960856 - Missing dependency: bitstream-vera-sans-fonts
- BZ 747421 - Move CGI executable from /usr/sbin to /usr/libexec
- BZ 796344 - Not compatible with JDK7
- BZ 846543 - mapserver-java is incorrectly packaged (missing required native library)
- trim of changelog

* Tue Apr 09 2013 Pavel Lisý <pali@fedoraproject.org> - 6.2.0-2
- changed MS_REL from 6x to 62

* Thu Apr 04 2013 Pavel Lisý <pali@fedoraproject.org> - 6.2.0-1
- Update to latest stable release
- dependency on bitstream-vera-sans-fonts replaced to dejavu-sans-fonts

* Mon Mar 25 2013 Oliver Falk <oliver@linux-kernel.at> - 6.0.3-10.1
- Rebuild - fix changelog (bogus date)

* Sat Mar 23 2013 Remi Collet <rcollet@redhat.com> - 6.0.3-10
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 6.0.3-8
- rebuild due to "jpeg8-ABI" feature drop

* Fri Oct 26 2012 Remi Collet <remi@fedoraproject.org> - 6.0.3-7
- conform to PHP Guidelines (#828161)
- add minimal load test for php extension

* Tue Oct 16 2012 Pavel Lisý <pali@fedoraproject.org> - 6.0.3-6
- temporary removed mapserver-java (mapscript) due to build problem
  with jdk7

* Fri Oct 12 2012 Pavel Lisý <pali@fedoraproject.org> - 6.0.3-5
- Merged from 6.0.3-4
- fix of build for php4 and swig > 2.0.4

* Tue Aug 14 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 6.0.3-4
- Rebuilt for new perl.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 10 2012 Petr Pisar <ppisar@redhat.com> - 6.0.3-2
- Perl 5.16 rebuild

* Sat Jun 30 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 6.0.3-1
- Update to 6.0.3, for various fixes described at:
  https://github.com/mapserver/mapserver/blob/rel-6-0-3-0/HISTORY.TXT
- Update URL, per bz #835426

* Fri Jun 08 2012 Petr Pisar <ppisar@redhat.com> - 6.0.2-2
- Perl 5.16 rebuild

* Mon Apr 16 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 6.0.2-1
- Update to 6.0.2, for various fixes described at:
  http://trac.osgeo.org/mapserver/browser/tags/rel-6-0-2/mapserver/HISTORY.TXT

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 6.0.1-4
- Rebuild for new libpng

* Thu Jul 21 2011 Petr Sabata <contyk@redhat.com> - 6.0.1-3
- Perl mass rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 6.0.1-2
- Perl mass rebuild

* Mon Jul 18 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 6.0.1-1
- Update to 6.0.1, for various fixes described at:
  http://trac.osgeo.org/mapserver/browser/tags/rel-6-0-1/mapserver/HISTORY.TXT
- Fixes bz #722545
- Apply changes to spec file for new major version.
