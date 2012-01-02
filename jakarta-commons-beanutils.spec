# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define with()          %{expand:%%{?with_%{1}:1}%%{!?with_%{1}:0}}
%define without()       %{expand:%%{?with_%{1}:0}%%{!?with_%{1}:1}}
%define bcond_with()    %{expand:%%{?_with_%{1}:%%global with_%{1} 1}}
%define bcond_without() %{expand:%%{!?_without_%{1}:%%global with_%{1} 1}}

%bcond_without jdk6
%bcond_with maven

%define _with_gcj_support 0
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define base_name       beanutils
%define short_name      commons-beanutils

%define section         free

Name:           jakarta-commons-beanutils
Version:        1.7.0
Release:        12.5%{?dist}
Epoch:          0
Summary:        Jakarta Commons BeanUtils Package
License:        ASL 2.0
Group:          Development/Libraries/Java
URL:            http://jakarta.apache.org/commons/%{base_name}/
Source0:        http://archive.apache.org/dist/commons/beanutils/source/commons-beanutils-1.7.0-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        commons-beanutils-1.7.0-jpp-depmap.xml
Source5:        commons-beanutils-1.7.0.pom
Source6:        commons-beanutils-bean-collections-1.7.0.pom
Source7:        commons-beanutils-core-1.7.0.pom
Source8:        commons-build.tar.gz
Source9:        commons-beanutils-maven.xml
Source10:       commons-beanutils-build-other-jars.xml
Source11:       jakarta-commons-beanutils-component-info.xml
Patch0:         commons-beanutils-1.7.0-project_xml.patch
Patch1:         commons-beanutils-1.7.0-BeanificationTestCase.patch
Patch2:         commons-beanutils-1.7.0-LocaleBeanificationTestCase.patch
Patch3:         commons-beanutils-1.7.0-navigation_xml.patch
Patch4:         commons-beanutils-1.7.0-project_properties.patch
Patch5:         commons-beanutils-1.7.0-jdk6.patch
BuildRequires:  ant
BuildRequires:  ant-junit
BuildRequires:  junit
%if %with maven
BuildRequires:  maven >= 0:1.1
BuildRequires:  maven-plugin-xdoc
BuildRequires:  saxon
BuildRequires:  saxon-scripts
%endif
BuildRequires:  jakarta-commons-collections >= 0:2.0
BuildRequires:  jakarta-commons-logging >= 0:1.0
BuildRequires:  java-1.6.0-devel
BuildRequires:  jpackage-utils > 0:1.7.2
BuildRequires:  coreutils
Requires:       jakarta-commons-collections >= 0:2.0
Requires:       jakarta-commons-logging >= 0:1.0
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
Provides:       %{short_name} = %{epoch}:%{version}-%{release}
Obsoletes:      %{short_name} < %{epoch}:%{version}-%{release}
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
%endif

%description
The scope of this package is to create a package of Java utility methods
for accessing and modifying the properties of arbitrary JavaBeans.  No
dependencies outside of the JDK are required, so the use of this package
is very lightweight.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation

%description javadoc
%{summary}.

%if %with maven
%package manual
Summary:        Documents for %{name}
Group:          Development/Documentation

%description manual
%{summary}.
%endif

%prep
%setup -q -n %{short_name}-%{version}-src
%setup -q -n %{short_name}-%{version}-src -T -D -a 8
cp -p %{SOURCE9} maven.xml
cp -p %{SOURCE10} build-other-jars.xml
#cp LICENSE.txt LICENSE
# remove all binary libs
# (dwalluck): jars are already removed
%patch0 -b .sav
%patch1 -b .sav
%patch2 -b .sav
%patch3 -b .sav
%patch4 -b .sav
%if %with jdk6
%patch5 -p1
%endif

%build
%if %with maven
if [ ! -f %{SOURCE4} ]; then
export DEPCAT=$(pwd)/commons-beanutils-1.7.0-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    %{_bindir}/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
%{_bindir}/saxon $DEPCAT %{SOURCE2} > commons-beanutils-1.7.0-depmap.new.xml
fi

for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    %{_bindir}/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done
mkdir -p .maven/repository/JPP/jars
mkdir -p .maven/plugins

export MAVEN_HOME_LOCAL=$(pwd)/.maven

maven -e \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=${MAVEN_HOME_LOCAL} \
        jar:jar site

%else
export CLASSPATH=$(build-classpath commons-collections commons-logging)
export OPT_JAR_LIST="ant/ant-junit junit"
ant -Dbuild.sysclasspath=first test dist
%endif

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
%if %with maven
install -m 644 target/%{short_name}-1.7.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -m 644 target/%{short_name}-bean-collections-1.7.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-bean-collections-%{version}.jar
install -m 644 target/%{short_name}-core-1.7.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-core-%{version}.jar
%else
install -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -m 644 dist/%{short_name}-core.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-core-%{version}.jar
install -m 644 dist/%{short_name}-bean-collections.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-bean-collections-%{version}.jar
%endif
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}
%add_to_maven_depmap %{short_name} %{short_name}-core %{version} JPP %{short_name}-core
%add_to_maven_depmap %{short_name} %{short_name}-bean-collections %{version} JPP %{short_name}-bean-collections

install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE5} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{short_name}.pom
install -pm 644 %{SOURCE6} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{short_name}-bean-collections.pom
install -pm 644 %{SOURCE7} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{short_name}-core.pom

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %with maven
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
# FIXME: (dwalluck): This breaks rpmbuild -bi --short-circuit
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/site
cp -p PROPOSAL.html STATUS.html RELEASE-NOTES.txt LICENSE.txt \
                 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%if %with maven
cp -pr target/docs/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/site
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- commons-beanutils < 1.7
pushd %{_javadir} > /dev/null
    ln -sf %{name}-%{version}.jar %{short_name}-%{version}.jar
    ln -sf %{short_name}-%{version}.jar %{short_name}.jar
popd > /dev/null

%post
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc *.html *.txt
%{_javadir}/*.jar
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jakarta-commons-beanutils-1.7.0.jar.*
# Not created by aot-compile for being subsets of the full JAR
#%attr(-,root,root) %{_libdir}/gcj/%{name}/jakarta-commons-beanutils-bean-collections-1.7.0.jar.*
#%attr(-,root,root) %{_libdir}/gcj/%{name}/jakarta-commons-beanutils-core-1.7.0.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%if %with maven
%files manual
%defattr(0644,root,root,0755)
%{_docdir}/%{name}-%{version}/site
%endif

%changelog
* Thu Jan 07 2010 Jeff Johnston <jjohnstn@redhat.com> 0:1.7.0-12.5
- Resolves: #553466
- Fix URL of source archive.

* Mon Dec 21 2009 Andrew Overholt <overholt@redhat.com> 0:1.7.0-12.4
- Remove gcj support.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.7.0-12.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.7.0-11.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-10.3
- Fedora-specific: enable GCJ support

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-10.2
- Fedora-specific: BuildRequires: java-1.6.0-devel

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-10.1
- Fedora-specific: remove repolib
- Fedora-specific: enable JDK6 support

* Mon Oct 20 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-10
- add flag to build with maven

* Fri Sep 19 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-9
- add jdk6 patch
- fix repolib

* Sun Jun 15 2008 David Walluck <dwalluck@redhat.com> 0:1.7.0-8.jpp5
- fix duplicate files
- correctly unpack sources
- remove spurious gnu-crypto requirement
- remove spurious javadoc package requirements
- fix javadoc directory
- fix build-classpath call
- use macros

* Fri May 30 2008 Permaine Cheung <pcheung@redhat.com> - 0:1.7.0-7
- First JPP5 build

* Tue Jul 24 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.7.0-6jpp
- Make Vendor, Distribution based on macro
- Fix aot build
- Add poms and depmap frags
- Build with maven1 by default
- Add manual subpackage when built with maven

* Tue Mar 13 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.7.0-2jpp.ep1.2
- Fix repolib location

* Tue Mar 13 2007 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-2jpp.ep1.1
- New repolib location

* Mon Mar 05 2007 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-2jpp.el4ep1.3
- Remove pre section used for RHUG cleanup

* Tue Feb 20 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.7.0-2jpp.el4ep1.2
- Add -brew suffix

* Fri Feb 17 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.7.0-2jpp.el4ep1.1
- Add repolib support

* Thu Aug 17 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-5jpp
- Require what is used in post/postun for javadoc

* Fri Jul 14 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-4jpp
- Add AOT bits

* Thu May 11 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-3jpp
- Add header
- Remove unecessary macro definitions

* Wed Feb 22 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-2jpp_1rh
- Merge with upstream

* Wed Apr 27 2005 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-1jpp_3rh
- Fix build so that collections jar is created

* Sat Jan 29 2005 Ralph Apel <r.apel@r-apel.de> - 0:1.7.0-2jpp
- Use the "dist" target to get a full build, including bean-collections

* Thu Oct 21 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-1jpp_1rh
- Import from upstream

* Thu Oct 21 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.7.0-1jpp
- Upgrade to 1.7.0

* Fri Oct 1 2004 Andrew Overholt <overholt@redhat.com> 0:1.6.1-4jpp_6rh
- add coreutils BuildRequires

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:1.6.1-5jpp
- Rebuild with ant-1.6.2

* Fri Jul 2 2004 Aizaz Ahmed <aahmed@redhat.com> 0:1.6.1-4jpp_5rh
- Added trigger to restore symlinks that are removed if ugrading
  from a commons-beanutils rhug package

* Fri Apr  2 2004 Frank Ch. Eigler <fche@redhat.com> 0:1.6.1-4jpp_4rh
- more of the same, for version-suffixed .jar files

* Fri Mar 26 2004 Frank Ch. Eigler <fche@redhat.com> 0:1.6.1-4jpp_3rh
- add RHUG upgrade cleanup

* Fri Mar  5 2004 Frank Ch. Eigler <fche@redhat.com> 0:1.6.1-4jpp_2rh
- RH vacuuming part II

* Thu Mar  4 2004 Frank Ch. Eigler <fche@redhat.com> 0:1.6.1-4jpp_1rh
- RH vacuuming

* Fri May 09 2003 David Walluck <david@anti-microsoft.org> 0:1.6.1-4jpp
- update for JPackage 1.5

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.6.1-2jpp
- fix ASF license and add packager name

* Wed Feb 19 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.6.1-1jpp
- 1.6.1

* Thu Feb 13 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.6-1jpp
- 1.6

* Thu Oct 24 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.5-1jpp
- 1.5

* Fri Aug 23 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.4.1-1jpp
- 1.4.1

* Tue Aug 20 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.4-1jpp
- 1.4

* Fri Jul 12 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.3-3jpp
- change to commons-xxx.jar instead of commons-xxx.home in ant parameters

* Mon Jun 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.3-2jpp
- use sed instead of bash 2.x extension in link area to make spec compatible
  with distro using bash 1.1x

* Fri Jun 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.3-1jpp 
- 1.3
- added short names in %%{_javadir}, as does jakarta developpers
- first jPackage release
