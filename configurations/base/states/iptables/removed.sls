iptables:
    pkg:
        - purge
    cron.rm:
        - user: root
        - special: '@reboot'
        - name: '/sbin/iptables-restore < /etc/iptables.up.rules'

'/etc/iptables-startup.sh && (md5sum /etc/iptables-startup.sh | cut -d " " -f 1 > /tmp/iptables.md5)':
    file:
        - absent
    crontab.absent:
        - name: '/sbin/iptables-restore < /etc/iptables.up.rules'
        - user: root

