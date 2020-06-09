Name: cockpit-ceph-installer
Version: 1.1
Release: 0%{?dist}
Summary: Cockpit plugin for Ceph cluster installation
License: LGPLv2+
URL: https://github.com/red-hat-storage/cockpit-ceph-installer

Source: ceph-installer-%{version}.tar.gz
BuildArch: noarch

Requires: ceph-ansible >= 4.0.14
Requires: cockpit
Requires: libcdio
Requires: cockpit-bridge

%if "%{?dist}" == ".el7" || "%{rhel}" == "7"
%define containermgr    docker
%else
%define containermgr    podman
%endif

Requires: %{containermgr}

%description
This package installs a cockpit plugin that provides a graphical interface to install a Ceph cluster. The plugin itself handles UI interaction and depends on the ansible-runner-service API to handle the configuration and management of the ansible inventory and playbooks.
In addition to the plugin, the installation process also enables docker/podman which is required for the ansible-runner-service API.

Once installed, a helper script called ansible-runner-service.sh is available to handle the installation and configuration of the ansible-runner-service daemon (container).

%prep
%setup -q -n ceph-installer-%{version}

%install
mkdir -p %{buildroot}%{_datadir}/cockpit/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/ceph-ansible/library
install -m 0644 dist/* %{buildroot}%{_datadir}/cockpit/%{name}/
install -m 0755 utils/ansible-runner-service.sh %{buildroot}%{_bindir}/
install -m 0644 utils/ansible/library/ceph_check_role.py %{buildroot}%{_datadir}/ceph-ansible/library/
install -m 0644 utils/ansible/checkrole.yml %{buildroot}%{_datadir}/ceph-ansible/
mkdir -p %{buildroot}%{_datadir}/metainfo/
install -m 0644 ./org.cockpit-project.%{name}.metainfo.xml %{buildroot}%{_datadir}/metainfo/


%post
if [ "$1" = 1 ]; then
  systemctl enable --now cockpit.service

# copy the ceph-ansible sample playbooks, so they're available to the runner-service
  cp %{_datadir}/ceph-ansible/site.yml.sample %{_datadir}/ceph-ansible/site.yml 
  cp %{_datadir}/ceph-ansible/site-docker.yml.sample %{_datadir}/ceph-ansible/site-docker.yml 
  cp %{_datadir}/ceph-ansible/site-docker.yml.sample %{_datadir}/ceph-ansible/site-container.yml 

# If this is a docker environment, start the daemon
  if  [ "%{containermgr}" == "docker" ]; then 
    systemctl enable --now %{containermgr}.service
  fi

fi

%files
%{_datadir}/cockpit/*
%{_datadir}/metainfo/*
%{_bindir}/ansible-runner-service.sh
%{_datadir}/ceph-ansible/library/ceph_check_role.py
%{_datadir}/ceph-ansible/checkrole.yml

# exclude the compiled/optimized py files generated by the helper scripts
%exclude %{_datadir}/ceph-ansible/library/*.pyo
%exclude %{_datadir}/ceph-ansible/library/*.pyc

%changelog
* Wed May 20 2020 Paul Cuzner <pcuzner@redhat.com> 1.1
- fix rounding issue of cpu requirement during host probe BZ 1794586
- fix text relating to filestore usage BZ1800664
- improve handling of existing ssh keys when using a sudo account BZ 1791143
- improve handling of more complex network configurations during the probe process BZ 1816478
- new: detect gpt disks during the probe
- switch rgw to beast frontend for Nautilus deployments BZ 1806791
- link the default ansible hosts to the runner-service inventory BZ 1814177
- make the runner-service pull command use the specific registry name BZ 1809003
- re-enable the back button after a deployment failure, so the config can be amended before rerun BZ 1809870
* Thu Jan 16 2020 Paul Cuzner <pcuzner@redhat.com> 1.0
- Minor UI fixes to correct capitalization of objectstore types
- Minor UI fixes to the tooltips on add hosts modal
- Fix to remove the beta tag from the container image names
- Fix to remove scroll bar from "add hosts" dialog
- Fix to allow roles to be modified in the hostspage
- fix to support ISO selection from multiple ISO image files
- updated tooltip text for firewalld ON/OFF setting
* Mon Dec 09 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-7
- skip adding iSCSI network info for Nautilus and above deployments
- added sudo support enabling a non-root user to drive the install process (with sudo privileges)
- fix the host-row-kebab menu missing issue, when user flips between hosts > validate > hosts
- info tip component shows more relevant information, particularly on the deploy page
- added firewall on/off widget to control the configuration of firewalld
- fix removal of last host in the hostspage
- fix to show error for hosts with /32 networks
- minor cosmetic changes to tooltip component
- Credentials input changed to align with using RH Registry Service Accounts (vs username/password)
- tooltip now supports hyperlinks (used to link out to RH service account information)
- added projects git url to the spec
* Mon Nov 04 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-6
- improve error message when ISO is selected without iso images being present 
- runtime settings are written to the cockpit users home directory to provide an installation audit record
- domain name now show in add hosts dialog 
- calculation of drive capacity for 4kN/512E drives improved
- Network subnet page usability improvements
* Tue Oct 22 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-5
- ensure repository_type is set correctly for redhat installs
- fix situation where the runner-service container wasn't shutdown cleanly
* Sun Oct 20 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-4
- include the ceph_docker_image var for rhcs deployments
* Thu Oct 17 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-3
- added tooltips to all the roles in the add-hosts modal
- added username and password fields to the environment page for rhcs/iso installs
- added rhcs specific container image names to all.yml
- added login credentials for registry.redhat.io to all.yml
- improve runner-service start up messages, and set container image defaults
- removed the prometheus port work around (handled in v4 of ceph-ansible)
- removed rhcs3 as an install option since this is an rhcs4 feature 
* Tue Oct 15 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-2
- improve handling of container image names that include a tag
- provide ceph.conf overrides for All-in-One clusters BZ1761616
- fix removal of runner-service container BZ1761608
- add missing iso directory to runner-service directory structure BZ1761610
* Sun Sep 15 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-1
- minor UI improvements
- add ISO installation option
- exclude loop back devices from device discovery in checkrole playbook (EL8 issue)
- fix port conflict when the metrics host is the same as the installer host
* Wed Jul 24 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-0
- ceph-check-role ansible module and playbook included
* Wed Jul 17 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-8
- remove ansible-runner-service rpm dependency
- handle podman/docker for el7/el8
- ensure the ansible-runner-service setup script is installed
* Thu Mar 21 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-7
- Return error if the probe task fails in some way
- Add visual cue (spinner) when the probe task is running
* Sun Mar 17 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-6
- Added 'save' step in deploy workflow, enabling ansible vars to be manually updated
* Sun Dec 16 2018 Paul Cuzner <pcuzner@redhat.com> 0.8
- Initial rpm build
- First functionally complete version