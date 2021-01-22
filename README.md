#Auto shelve server
This script will auto shelve intances in OpenStack after a configurable number of days.

When the script first runs, it will pull all instances form the openstacksdk and then tag metadata with key retire_date (now + x days).
Next, run of the script, it will check the metadata retire_date key and if it its exceeded, it will shelve the server and send a notification email user
The user us lookup in Active Directory using LDAP. 


# Installation
````
apt install python3-openstacksdk python3-ldap
````


# Trouble shooting
Verify timer is running:
````
oot@os-infra-c-01-utility-container-09bb929c:/opt/openstack-auto-shelve-instance# systemctl list-timers
NEXT                        LEFT           LAST                        PASSED       UNIT                         ACTIVATES
Fri 2021-01-22 08:48:02 UTC 1h 37min left  Thu 2021-01-21 08:48:02 UTC 22h ago      systemd-tmpfiles-clean.timer systemd-tmpfiles-clean.service
Fri 2021-01-22 14:09:47 UTC 6h left        Fri 2021-01-22 07:07:21 UTC 2min 41s ago motd-news.timer              motd-news.service
Fri 2021-01-22 22:00:13 UTC 14h left       Fri 2021-01-22 07:09:09 UTC 53s ago      apt-daily.timer              apt-daily.service
Sat 2021-01-23 00:00:00 UTC 16h left       Fri 2021-01-22 00:00:02 UTC 7h ago       auto_shelve_server.timer     auto_shelve_server.service
Sat 2021-01-23 00:00:00 UTC 16h left       Fri 2021-01-22 00:00:02 UTC 7h ago       logrotate.timer              logrotate.service
Sat 2021-01-23 06:25:18 UTC 23h left       Fri 2021-01-22 06:54:02 UTC 16min ago    apt-daily-upgrade.timer      apt-daily-upgrade.service
Sun 2021-01-24 03:10:49 UTC 1 day 20h left Sun 2021-01-17 03:11:02 UTC 5 days ago   e2scrub_all.timer            e2scrub_all.service

7 timers listed.
Pass --all to see loaded but inactive timers, too.
root@os-infra-c-01-utility-container-09bb929c:/opt/openstack-auto-shelve-instance#
````

Retreive logs:
````
journalctl -f 

Jan 22 07:11:27 os-infra-c-01-utility-container-09bb929c systemd[1]: Starting Auto shelve instance...
Jan 22 07:11:28 os-infra-c-01-utility-container-09bb929c systemd[1]: auto_shelve_server.service: Succeeded.
Jan 22 07:11:28 os-infra-c-01-utility-container-09bb929c systemd[1]: Finished Auto shelve instance.
````
Verify the auto_shelve_server.service is successful.

You can invoke it manually with:
````
systemctl start auto_shelve_server.service
````
