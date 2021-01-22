#!/bin/bash
cp auto_shelve_server.service /etc/systemd/system/
cp auto_shelve_server.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable auto_shelve_server.service
systemctl enable auto_shelve_server.timer
systemctl start auto_shelve_server.service
systemctl start auto_shelve_server.timer