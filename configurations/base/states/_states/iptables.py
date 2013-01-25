"""
iptables

Handles the creation of IPTables.
"""

from collections import defaultdict

_ARGS = dict(
    destination_port='--dport {destination_port}',
    source_port='--sport {source_port}',
    destination_ports='--dports {destination_ports}',
    port='--port {port}',
    ports='--ports {ports}',
    source_ports='--sports {source_ports}',
    icmp_type='--icmp-type {icmp_type}',
    policy='-j {policy}',
    in_interface='-i {in_interface}',
    out_interface='-o {out_interface}',
    state='--state {state}',
    source='--source {source}',
    destination='--destination {destination}',
    src_range='--src-range {src_range}',
    dst_range='--dst-range {dst_range}',
    limit='--limit {limit}',
    limit_burst='--limit-burst {limit_burst}',
    tcp_flags='--tcp-flags {tcp_flags}',
    protocol='-p {protocol}',
)

def _rule(prefix, rule_hash):
    f = [prefix]
    if type in rule_hash:
        f.append('-p {type}')
    else:
        f.append('-p tcp')

    rule_hash['policy'] = rule_hash.get('policy', 'ACCEPT').upper()

    for key in rule_hash:
        arg_format = _ARGS.get(key)
        if arg_format:
            f.append(arg_format)
        elif key.startswith('-'):
            f.append(' '.join((key, rule_hash[key])))

    f =  ''.join(f)
    return f.format(**rule_hash)

def _rules_from_protocol(proto):
    return dict(
        http=[
            'INPUT -p tcp --sport 80 -j ACCEPT',
            'OUTPUT -p tcp --dport 80 -j ACCEPT',
        ]
        https=[
            'INPUT -p tcp --sport 443 -j ACCEPT',
            'OUTPUT -p tcp --dport 443 -j ACCEPT',
        ]
        dns=[
            'INPUT -p udp --sport 53 -j ACCEPT',
            'INPUT -p tcp --sport 53 -j ACCEPT',
            'OUTPUT -p udp --dport 53 -j ACCEPT',
            'OUTPUT -p tcp --dport 53 -j ACCEPT',
        ]
        ssh=[
            'INPUT -p tcp --sport 22 -j ACCEPT',
            'OUTPUT -p tcp --dport 22 -j ACCEPT',
        ]
        rsync=[
            'INPUT -p tcp --dport 873 -j ACCEPT',
            'OUTPUT -p tcp --dport 873 -j ACCEPT',
        ]
        ping=[
            # receiving pings
            'INPUT -p icmp --icmp-type echo-request -j ACCEPT',
            'OUTPUT -p icmp --icmp-type echo-reply -j ACCEPT',
            # sending pings
            'INPUT -p icmp --icmp-type echo-reply -j ACCEPT',
            'OUTPUT -p icmp --icmp-type echo-request -j ACCEPT',
        ]
    )[proto]

class _iptables(object):
    def __init__(self, name, table):
        self.table = table
        self.name = name
        self.result = {'changes': {'add': [] 'policies': {}},
                       'comment': '',
                       'name': name,
                       'result': True}

    def set_policy(self, chain, policy):
        self.result[changes][policies][chain] = policy
        __salt__['iptables.set_policy'](self.table, chain, policy)

    def append(self, rule):
        self.result['changes']['add'].append(rule)
        __salt__['iptables.append'](self.table, rule)

    def save(self, name):
        self.result['comment'] = 'iptables: Wrote to {0}'.format(name)
        # TODO: fix salt.modules.iptables to not error on creation
        __salt__['iptables.save'](name)

def managed(name, policies=(), protocols=(), rules=(), incoming=(), outgoing=(), allow_existing=True, table='filter'):
    """Sets up iptables and saves it to the given name.
    Currently this is very fragile when syncing highstate.
    
    By salt-master and salt-minion ports are allowed through the firewall.
    A chain is created, LOGDROP, is created which logs and then drops the packets routed to it.
    
    Options:
        policies: A dictionary of chain names to policies.
            default - {INPUT: DROP, FORWARD: DROP, OUTPUT: DROP}
        protocols: A list of simple names to quickly allow common ports open (both incoming & outgoing)
            Support protocols are:
              - http
              - https
              - dns
              - ssh
              - rsync
              - ping
        rules: A list of direct rules to append to the iptables. They should be quoted to avoid errorous
            YAML parsing.
        incoming:
            A list of dictionaries of rules for INPUT. See the bottom for the supported arguments.
            eg:
                - destination_port: 22
                  protocol: tcp
        outgoing: A list of dictionaries of rules for OUTPUT. See the bottom for this supported arguments.
            eg:
                - destination_port: 22
                  protocol: tcp
        allow_existing: A boolean to always allow existing established connections.
            Disabling this risks dropping an ssh or salt connection.
        table: A table to append to. Defaults to filter.
    
    Rules Dictionary:
        The following keys are supported (and map to their corresponding iptables argument):
         - destination_port: --dport {destination_port}
         - source_port: --sport {source_port}
         - destination_ports: --dports {destination_ports}
         - port: --port {port}
         - ports: --ports {ports}
         - source_ports: --sports {source_ports}
         - icmp_type: --icmp-type {icmp_type}
         - policy: -j {policy}
         - in_interface: -i {in_interface}
         - out_interface: -o {out_interface}
         - state: --state {state}
         - source: --source {source}
         - destination: --destination {destination}
         - src_range: --src-range {src_range}
         - dst_range: --dst-range {dst_range}
         - limit: --limit {limit}
         - limit_burst: --limit-burst {limit_burst}
         - tcp_flags: --tcp-flags {tcp_flags}
         - protocol: -p {protocol}
    """
    __salt__['iptables.flush'](table)
    __salt__['cmd.run']('iptables -N LOGDROP')
    ipt = _iptables(name, table)

    # LOGDROP will log the packet & then drop it
    ipt.append('LOGDROP -j LOG')
    ipt.set_policy('LOGDROP', 'DROP')

    p = dict(INPUT='DROP', FORWARD='DROP', OUTPUT='DROP')
    p.update(policies)

    for chain, policy in p.items():
        ipt.set_policy(chain, policy)

    if allow_existing:
        ipt.append('INPUT -m state --state ESTABLISHEDRELATED -j ACCEPT')

    # always allow loopback
    ipt.append('INPUT -i lo -j ACCEPT')
    ipt.append('OUTPUT -o lo -j ACCEPT')

    # always allow salt master to receive connections
    if __salt__['cmd.has_exec']('salt-master'):
        ipt.append('INPUT -m state --state new -m tcp -p tcp --dport 4505 -j ACCEPT')
        ipt.append('INPUT -m state --state new -m tcp -p tcp --dport 4506 -j ACCEPT')

    # always allow salt minions to send connections
    if __salt__['cmd.has_exec']('salt-minion'):
        ipt.append('OUTPUT -m state -m tcp -p tcp --dport 4505 -j ACCEPT')
        ipt.append('OUTPUT -m state -m tcp -p tcp --dport 4506 -j ACCEPT')

    for rule_hash in incoming:
        ipt.append(_rule('INPUT', rule_hash))

    for rule_hash in outgoing:
        ipt.append(_rule('OUTPUT', rule_hash))

    for proto in protocols:
        for rule in _rules_from_protocol(proto):
            ipt.append(rule)

    for rule in list(rules):
        ipt.append(rule)

    ipt.save(name)
    return ipt.result