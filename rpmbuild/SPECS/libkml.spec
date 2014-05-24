Name:           libkml
Version:        1.1.0
Release:        1%{?dist}
Summary:        LIBKML

Group:          Development/Libraries
License:        BSD
URL:            https://github.com/google/libkml/
Source:         https://github.com/google/libkml/archive/libkml-%{version}.tar.gz

BuildRequires:  expat-devel file curl-devel zlib-devel


%description
libkml library

%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
Development files for %{name}.

%package python
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description python
Python module for %{name}.


%prep
%setup -q
./autogen.sh

%build
./configure \
  --prefix=%{buildroot}%{_prefix} \
  --libdir=%{buildroot}%{_libdir} \
  --disable-rpath \
  --with-java-include-dir=/usr/lib/jvm/java/include \
  --with-java-lib-dir=/usr/lib/jvm/java/lib
# https://fedoraproject.org/wiki/Packaging:Guidelines?rd=PackagingGuidelines#Beware_of_Rpath
##
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

%install

make install
# Attempt to fix *.la files for libdir
##
cd %{buildroot}/%{_libdir}
# Yank any %{buildroot} references
##
find . -name \*.la -exec sed -i 's|%{buildroot}||g' {} \;

%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files
#%doc README
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so*
%{_libdir}/libkml/*.so*
%{_libdir}/libkml/*.a
%{_libdir}/libkml/*.la
/usr/share/java/*.jar

%files devel
%{_includedir}/kml/*.h
%{_includedir}/kml/base/*.h
%{_includedir}/kml/xsd/*.h
%{_includedir}/kml/engine/*.h
%{_includedir}/kml/regionator/*.h
%{_includedir}/kml/dom/*.h
%{_includedir}/kml/convenience/*.h
%{_includedir}/kml/third_party/boost_1_34_1/boost/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/config/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/config/compiler/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/config/no_tr1/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/config/platform/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/config/stdlib/*.hpp
%{_includedir}/kml/third_party/boost_1_34_1/boost/detail/*.hpp

%files python
%{_libdir}/python2.7/site-packages/*kml*


%changelog
* Mon May 19 2014 Rob Cermak <rob.cermak@gmail.com> - 1.1.0
- Create an rpm out of libkml

