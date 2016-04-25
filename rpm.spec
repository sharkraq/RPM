Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        EdgeOS Scanner and NeXpose

Group:          Vuma
License:         Systems AI
URL:   		http://www.systems.com/
Source0:	scanner.tar
Source1:	NeXposeSetup-Linux64.bin
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot

Requires: screen nmap openvpn PyYAML python-pycurl dialog jwhois bind-utils hping tcptraceroute       

%description
The EdgeOS Scanner and NeXpose

%prep

%build

%pre
if [[ $1 = 1 ]]; then
echo "Initial Install"  
elif [[ $1 = 2 ]]; then
echo "Starting update"
service nexposeengine.rc stop
cd /
tar cvf /var/upgrade-backup.tar /etc/scanner.conf /scanner/etc/portal-key /scanner/etc/scanner-id /scanner/etc/vpn_ip /etc/openvpn \
/opt/rapid7/nexpose/nse/conf /opt/rapid7/nexpose/nse/db /opt/rapid7/nexpose/nse/keystores /opt/rapid7/nexpose/nse/logs /opt/rapid7/nexpose/nse/scheduler \
--ignore-failed-read

/opt/rapid7/nexpose/.install4j/uninstall << EOF
y
EOF
fi

%install
if [ ! -d %{buildroot}/scanner ]; then
mkdir -p %{buildroot}/scanner %{buildroot}/etc/ssl/certs %{buildroot}/opt/rapid7/nexpose/nse/conf \
%{buildroot}/scanner/tmp %{buildroot}/scanner/log %{buildroot}/scanner/tmp  %{buildroot}/etc/cron.d \
%{buildroot}/usr/lib/python2.6/site-packages
fi

tar xvf %{SOURCE0} -C %{buildroot}/scanner 

cat << EOF > %{buildroot}/scanner/etc/internal.conf
[Global]

tmp_dir:string                          = /scanner/tmp
EOF

cp %{SOURCE1} %{buildroot}/scanner/tmp

chmod -R 755 %{buildroot}/scanner/bin
chmod -R 755 %{buildroot}/scanner/lib
cp -r  %{buildroot}/scanner/lib/python/web.py %{buildroot}/scanner/web.py
cp -r %{buildroot}/scanner/rpm_files/scanner-checkin-ca.crt %{buildroot}/etc/ssl/certs/scanner-checkin-ca.crt
cp -r %{buildroot}/scanner/rpm_files/consoles.xml %{buildroot}/opt/rapid7/nexpose/nse/conf/consoles.xml
echo -n %{iso_version} > %{buildroot}/scanner/etc/iso-version
echo -n "0" > %{buildroot}/scanner/etc/scanner-id
chmod 755  %{buildroot}/scanner/tmp %{buildroot}/scanner/log
chmod 600 %{buildroot}/scanner/etc/scanner-sanity-key %{buildroot}/scanner/etc/internal.conf
touch %{buildroot}/scanner/tmp/first-time
touch %{buildroot}/scanner/tmp/booting
touch %{buildroot}/scanner/etc/hdinstall
cp %{buildroot}/scanner/etc/cron %{buildroot}/etc/cron.d/scanner
ln -sf /scanner/lib/python %{buildroot}/usr/lib/python2.6/site-packages/scanner
ln -sf /scanner/lib/asset %{buildroot}/usr/lib/python2.6/site-packages/asset
echo "scanner package installed"

%clean

%files
%defattr(-,root,root,-)
%doc
/etc/cron.d/scanner
/etc/ssl/certs/scanner-checkin-ca.crt
/usr/lib/python2.6/site-packages/asset
/usr/lib/python2.6/site-packages/scanner
/scanner/
/opt/rapid7/nexpose/nse/conf/consoles.xml

%post
/sbin/chkconfig --level 2345 openvpn on

portalResult=`grep "scannerportal.vuma.silversky.com" /etc/hosts`
rc=$?
if [ $rc == 1 ]; then
  echo "165.212.169.143 portal scannerportal.vuma.silversky.com" >>/etc/hosts
else
  oldPortalIp=`echo $portalResult|awk '{print $1;}'`
  sed -i -e "s/${oldPortalIp}/"165.212.169.143"/g" /etc/hosts
fi

sh /scanner/tmp/NeXposeSetup-Linux64.bin -q -overwrite -Vfirstname='Drew' -Vlastname='Liao' -Vcompany='BAE' -Vusername='aliao' -Vpassword1='Daybreak_1' -Vpassword2='Daybreak_1' -Vsys.component.typical\$Boolean=false -Vsys.component.engine\$Boolean=true -VinitService\$Boolean=false -Dinstall4j.suppressUnattendedReboot=true
/sbin/service nexposeengine.rc start

if [[ $1 = 2 ]]; then
service  nexposeengine.rc stop
cd /
tar xvf /var/upgrade-backup.tar
/sbin/service  nexposeengine.rc start
fi

rm /scanner/tmp/NeXposeSetup-Linux64.bin

%preun
if [[ $1 = 0 ]]; then
echo "Removing rpm"  
service  nexposeengine.rc stop
/opt/rapid7/nexpose/.install4j/uninstall << EOF
y
EOF
fi
%postun

%changelog
* Wed Jan 20 2016 <malvarenga@silversky.com> 
- Initial Build.
