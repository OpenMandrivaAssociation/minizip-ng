%global optflags %{optflags} -O3

# (tpg) enable PGO build
%ifnarch riscv64
%bcond_without pgo
%else
%bcond_with pgo
%endif

%define major 3
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Zip manipulation library
Name:		minizip-ng
Version:	3.0.3
Release:	2
License:	zlib
Group:		System/Libraries
Url:		https://github.com/zlib-ng/minizip-ng
Source0:	https://github.com/zlib-ng/minizip-ng/archive/%{version}/%{name}-%{version}.tar.gz
Patch0:		minizip-ng-dont-use-zlib-and-zlib-ng-at-the-same-time.patch
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(zlib-ng)
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(openssl)

%description
minizip-ng is a zip manipulation library written in C
that is supported on Windows, macOS, and Linux.

%package -n %{libname}
Summary:	%{summary}
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
%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-instr-generate" \
%cmake \
    -DMZ_BUILD_TESTS=ON \
    -DMZ_COMPAT:BOOL=ON \
    -G Ninja

%ninja_build

LD_PRELOAD=./libminizip.so ./test_cmd

unset LD_LIBRARY_PATH
llvm-profdata merge --output=../%{name}-llvm.profdata *.profraw
PROFDATA="$(realpath ../%{name}-llvm.profdata)"
rm -rf *.profraw
ninja clean
cd ..
rm -rf build

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%cmake \
    -DMZ_COMPAT:BOOL=ON \
    -DINSTALL_INC_DIR:PATH=%{_includedir}/minizip \
    -G Ninja

%ninja_build

%install
%ninja_install -C build

# For compatibilibty with old minizip
ln -s mz_compat.h %{buildroot}%{_includedir}/minizip/ioapi.h

%files -n %{libname}
%{_libdir}/libminizip.so.%{major}*

%files -n %{develname}
%{_includedir}/minizip
%dir %{_libdir}/cmake/minizip
%{_libdir}/cmake/minizip/*.cmake
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc
