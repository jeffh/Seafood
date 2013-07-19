#!/bin/sh
/sbin/iptables-restore < {{ rules }}
exit 0