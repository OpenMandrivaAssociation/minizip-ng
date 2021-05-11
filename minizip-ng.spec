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
Version:	3.0.1
Release:	4
License:	zlib
Group:		System/Libraries
Url:		https://github.com/zlib-ng/minizip-ng
Source0:	https://github.com/zlib-ng/minizip-ng/archive/%{version}/%{name}-%{version}.tar.gz
Patch0:		minizip-ng-dont-use-zlib-and-zlib-ng-at-the-same-time.patch
# https://github.com/zlib-ng/minizip-ng/issues/566
Patch1:		https://github.com/zlib-ng/minizip-ng/commit/8847f22979f76e53bf55c802a1cd26f8edd6a326.patch
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
%if %{with pgo}
CFLAGS="%{optflags} -fprofile-instr-generate"
CXXFLAGS="%{optflags} -fprofile-instr-generate"
FFLAGS="$CFLAGS"
FCFLAGS="$CFLAGS"
LDFLAGS="%{build_ldflags} -fprofile-instr-generate"
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"

%cmake \
    -DMZ_BUILD_TESTS=ON \
    -DMZ_COMPAT:BOOL=ON \
    -G Ninja

%ninja_build

LD_PRELOAD=./libminizip.so ./test_cmd

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=../%{name}.profile *.profile.d
rm -f *.profile.d
ninja clean
cd ..
rm -rf build

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%cmake \
    -DMZ_COMPAT:BOOL=ON \
    -DINSTALL_INC_DIR:PATH=%{_includedir}/minizip \
    -G Ninja

%ninja_build

%install
%ninja_install -C build

%files -n %{libname}
%{_libdir}/libminizip.so.%{major}*

%files -n %{develname}
%{_includedir}/minizip
%dir %{_libdir}/cmake/minizip
%{_libdir}/cmake/minizip/*.cmake
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc
