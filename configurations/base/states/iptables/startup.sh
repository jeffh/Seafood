#!/bin/bash

# Based on http://serverfault.com/questions/245711/iptables-tips-tricks/245713#245713
# Managed by Salt
set -e
IPTABLES=/sbin/iptables

WHITELIST="{% for ip in whitelist %}{{ ip }}{% if not loop.last %} {% endif %}{% endfor %}"
BLACKLIST="{% for ip in blacklist %}{{ ip }}{% if not loop.last %} {% endif %}{% endfor %}"
ALLOWED_TCP="{% for p in allowed_tcp %}{{ p }}{% if not loop.last %} {% endif %}{% endfor %}"
ALLOWED_UDP="{% for p in allowed_udp %}{{ p }}{% if not loop.last %} {% endif %}{% endfor %}"

# clear all rules
$IPTABLES --flush
$IPTABLES --delete-chain
echo "Flushed iptables"

$IPTABLES -A INPUT -i lo -p all -j ACCEPT
$IPTABLES -A OUTPUT -o lo -p all -j ACCEPT
echo "Allowing loopback interface"

$IPTABLES -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables denied: " --log-level 7
echo "Set logging of denied packets"

echo "Set whitelist"
# IP-Address Whitelist
for x in $WHITELIST; do
        $IPTABLES -A INPUT -t filter -s $x -j ACCEPT
        echo " - $x"
done

echo "Set blacklist"
# IP-Address Blacklist
for x in $BLACKLIST; do
        $IPTABLES -A INPUT -t filter -s $x -j DROP
        echo " - $x"
done

echo "Set allowed TCP ports"
# Allowed TCP ports
for port in $ALLOWED_TCP; do
       $IPTABLES -A INPUT -t filter -p tcp --dport $port -j ACCEPT
       echo " - $port"
done

echo "Set allowed UDP ports"
# Allowed UDP Ports
for port in $ALLOWED_UDP; do
        $IPTABLES -A INPUT -t filter -p udp --dport $port -j ACCEPT
        echo " - $port"
done

# existing connections get a pass
$IPTABLES -A INPUT -m state --state ESTABLISHED -j ACCEPT

# Block XMAS packets
$IPTABLES -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
echo "Blocked XMAS packets"

# Reject spoofed packets
# These adresses are mostly used for LAN's, so if these would come to a WAN-only server, drop them.
# $IPTABLES -A INPUT -s 10.0.0.0/8 -j DROP
# $IPTABLES -A INPUT -s 169.254.0.0/16 -j DROP
# $IPTABLES -A INPUT -s 172.16.0.0/12 -j DROP
# $IPTABLES -A INPUT -s 127.0.0.0/8 -j DROP
# 
# echo "Blocked spoofed packets"

# ignore multicast-addresses
$IPTABLES -A INPUT -s 224.0.0.0/4 -j DROP
$IPTABLES -A INPUT -d 224.0.0.0/4 -j DROP
$IPTABLES -A INPUT -s 240.0.0.0/5 -j DROP
$IPTABLES -A INPUT -d 240.0.0.0/5 -j DROP
$IPTABLES -A INPUT -s 0.0.0.0/8 -j DROP
$IPTABLES -A INPUT -d 0.0.0.0/8 -j DROP
$IPTABLES -A INPUT -d 239.255.255.0/24 -j DROP
$IPTABLES -A INPUT -d 255.255.255.255 -j DROP

echo "Blocked multicast"

# ignore all invalid packets
$IPTABLES -A INPUT -m state --state INVALID -j DROP
$IPTABLES -A FORWARD -m state --state INVALID -j DROP
$IPTABLES -A OUTPUT -m state --state INVALID -j DROP

echo "Blocked invalid packets"

# Stop smurf attacks
$IPTABLES -A INPUT -p icmp -m icmp --icmp-type address-mask-request -j DROP
$IPTABLES -A INPUT -p icmp -m icmp --icmp-type timestamp-request -j DROP

$IPTABLES -A INPUT -p icmp -j DROP
echo " - Blocked ICMP"

# Drop excessive RST packets to avoid smurf attacks
$IPTABLES -A INPUT -p tcp -m tcp --tcp-flags RST RST -m limit --limit 2/second --limit-burst 2 -j ACCEPT
echo "Blocked smurf attacks"

# Don't allow pings through
$IPTABLES -A INPUT -p icmp -m icmp --icmp-type 8 -j DROP

echo "Require SYN for new connections"

# force fragment packet checking
$IPTABLES -A INPUT -f -j DROP
echo "Require fragment packet checking"

# default policies
$IPTABLES -P INPUT {{ policy.get('input', 'DROP').upper() }}
$IPTABLES -P FORWARD {{ policy.get('forward', 'ACCEPT').upper() }}
$IPTABLES -P OUTPUT {{ policy.get('output', 'ACCEPT').upper() }}
echo "Set default policies"