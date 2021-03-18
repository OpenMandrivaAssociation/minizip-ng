%global optflags %{optflags} -O3

%define major 3
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Zip manipulation library
Name:		minizip-ng
Version:	3.0.1
Release:	1
License:	zlib
Group:		System/Libraries
Url:		https://github.com/zlib-ng/minizip-ng
Source0:	https://github.com/zlib-ng/minizip-ng/archive/%{version}/%{name}-%{version}.tar.gz
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(openssl)

%description
minizip-ng is a zip manipulation library written in C
that is supported on Windows, macOS, and Linux.

%package -n %{libname}
Summary:	%{symmary}
Group:		System.Libraries

%description -n %{libname}
%{description}

%package -n %{develname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}

%description -n %{develname}
Developemt files and headers for %{name}.

%prep
%autosetup -p1

%build
%cmake \
    -G Ninja

%ninja_build

%install
%ninja_install -C build

%files -n %{libname}
%{_libdir}/libminizip.so.%{major}*

%files -n %{develname}
%{_includedir}/*.h
%dir %{_libdir}/cmake/minizip
%{_libdir}/cmake/minizip/*.cmake
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc
