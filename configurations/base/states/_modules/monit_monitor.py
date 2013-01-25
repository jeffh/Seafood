# TODO: incomplete. only supports reading of monit config files
# need to support writing to /etc/monit/conf.d/*.conf
import os
import re
import logging
import urlparse
from collections import defaultdict

from salt.modules.service import grainmap

# for monit, if is a noise keyword
# but parsing will be easier for use if we parse 'if's
NOISE_KEYWORDS = set('and with within has using use on only usage program programs'.split(' '))
ENTRY_KEYWORDS = set('if else group depends start stop'.split(' '))
start_keywords = set(['set', 'check', 'include'])

logger = logging.getLogger(__name__)


def __virtual__():
    if __salt__['cmd.has_exec']('monit'):
        return 'monitor'
    return False

def _pop(tokens):
    while tokens[0] in NOISE_KEYWORDS:
        tokens.pop(0)
    return tokens.pop(0)

def _consume_until(tokens, token_set):
    t = tokens[0]
    consumed = []
    token_set = set(token_set)
    while tokens and t.lower() not in token_set:
        consumed.append(t)
        tokens.pop(0)
        if tokens:
            t = tokens[0]
    return consumed
    
def _read_actions(tokens):
    valid_actions = set('alert restart start stop exec monitor unmonitor'.split(' '))
    actions = []
    stop_words = ENTRY_KEYWORDS.union(start_keywords)
    while tokens and tokens[0].lower() in valid_actions:
        action = tokens[0].lower()
        ret = {'name': _pop(tokens)}
        if action == 'exec':
            ret['file'] = _pop(tokens)
            items = _consume_until(tokens, ENTRY_KEYWORDS)
            ret.update(dict(zip(items[::2], items[1::2])))
        elif action == 'alert' and tokens and tokens[0] not in stop_words:
            ret['action'] = _pop(tokens)
            ret['extra'] = ' '.join(_consume_until(tokens, stop_words))
        actions.append(ret)
    if not actions:
        return [{'_error': 'Failed to parse "{0}"'.format(action), '_action': 'read_actions'}]
    return actions
    
def _read_service_entry(tokens):
    accum = []
    while tokens and tokens[0] not in ('set', 'check', 'include'):
        entry = _pop(tokens).lower()
        logger.info("Read Service Entry Token: {0}".format(repr(entry)))
        if entry == 'if':
            ret = {'if': ' '.join(_consume_until(tokens, set(['then'])))}
            if tokens[0].lower() == 'then':
                tokens.pop(0)
            ret.update({'then': _read_actions(tokens)})
            accum.append(ret)
        elif entry == 'else':
            ret = _read_service_entry(tokens)
            ret['else'] = ret['if']
            del ret['if']
            accum.append(ret)
        elif entry == 'start':
            accum.append({'start': tokens.pop(0)})
        elif entry == 'stop':
            accum.append({'stop': tokens.pop(0)})
        elif entry == 'group':
            accum.append({'group': _pop(tokens)})
        elif entry == 'depends':
            accum.append({'depends': ' '.join(_consume_until(tokens, ENTRY_KEYWORDS))})
        elif entry in ('start', 'stop'):
            accum.append({entry: _consume_until(tokens, ENTRY_KEYWORDS)})
        else:
            raise Exception('Parse Error: Unknown service entry {0}'.format(repr(entry)))
    return accum
    
def list(filepath='/etc/monit/monitrc'):
    "Returns a data structure from the monit file."
    with open(filepath, 'r') as h:
        # remove comments and newlines
        contents = re.sub(r'(?m)#.*$', '', h.read())
    
    ret = {'sets': {}, 'includes': [], 'checks': []} # checks go here
    
    # split by check keyword
    tokens = [tok for tok in re.split(r'[\r\n\t ]+', contents) if tok]
    while tokens:
        token = _pop(tokens)
        logger.info("READ: {0}".format(repr(token)))
        token_lower = token.lower()
        if token_lower == 'check':
            item = {
                'check': _pop(tokens),
                'name': _pop(tokens),
            }
            if item['check'].lower() != 'system':
                key = _pop(tokens).lower()
                value = _pop(tokens)
                item[key] = value
            logger.info("CHECK: {0}".format(repr(item)))
            item['rules'] = _read_service_entry(tokens)
            ret['checks'].append(item)
        elif token_lower == 'include':
            ret['includes'].append(_pop(tokens))
        elif token_lower == 'set':    
            key, value = _pop(tokens), ' '.join(_consume_until(tokens, start_keywords))
            item = {key: value}
            ret['sets'].update(item)
        elif token:
            logger.warn('Parse Error: Unknown token {0}'.format(repr(token)))
    return ret

def _serialize_actions(actions):
    def d(v):
        dic = {'action': '', 'extra': ''}
        dic.update(v)
        return dic
    return '\n'.join('{name} {action} {extra}'.format(**d(action)) for action in actions).strip()
    
def _serialize(data):
    sb = ['# Managed by Salt']
    for key, value in data['sets'].items():
        sb.append('set {0} {1}'.format(key, value))
        
    for service in data['checks']:
        sb.append('')
        sb.append('check {0} {1}'.format(service['check'], service['name']))
        if 'path' in data:
            sb.append('with path {0}'.format(data['path']))
        elif 'address' in data:
            sb.append('with address {0}'.format(data['address']))
        elif 'pidfile' in data:
            sb.append('with pidfile {0}'.format(data['path']))
        for rule in service['rules']:
            if 'if' in rule:
                sb.append('if {0} then {1}'.format(rule['if'], _serialize_actions(rule['then'])))
            elif 'else' in rule:
                sb.append('else if {0} then {1}'.format(rule['else'], _serialize_actions(rule['then'])))
            elif 'group' in rule:
                sb.append('group {group}'.format(**rule))
            elif 'depends' in rule:
                sb.append('depends {depends}'.format(**rule))
            elif 'start' in rule:
                sb.append('start {start}'.format(**rule))
            elif 'stop' in rule:
                sb.append('stop {stop}'.format(**rule))
    
    sb.append('')
    for path in data['includes']:
        sb.append('include {0}'.format(path))
    return '\n'.join(sb)
    
def _write_file(filename, monit_conf):
    with open(filename, 'w+') as h:
        h.write(_serialize(monit_conf))

_PROTOCOLS = {
    'https': 'type TCPSSL protocol HTTP',
    'http': 'protocol HTTP',
    'ssl': 'type TCPSSL',
    'udp': 'type UDP',
    'tcp': 'type TCP',
    'memcache': 'protocol MEMCACHE',
    'apache': 'protocol APACHE-STATUS',
    'mysql': 'protocol MYSQL',
    'imap': 'protocol IMAP',
    'nntp': 'protocol NNTP',
    'dns': 'protocol DNS',
    'ftp': 'protocol FTP',
    'rsync': 'protocol rsync',
    'stmp': 'protocol STMP',
    'ssh': 'protocol SSH',
    'PGSQL': 'protocol PGSQL',
}

def _parse_socket(url):
    result = []
    uri = urlparse.urlparse(monitor['http'])
    if uri.hostname:
        result.append('host {0}'.format(uri.hostname))
    if uri.port:
        result.append('port {0}'.format(uri.port))

    scheme = uri.scheme.lower()
    proto = _PROTOCOLS.get(scheme)
    if proto:
        result.append(proto)

    if uri.path not in ('', '/'):
        result.append('request {0}'.format(repr(uri.path)))
    return ' '.join(result)

def _parse(condition, action):
    result = {}
    if 'http' in monitor:
        result['if'] = 'failed ' + _parse_http(monitor['http'])
    elif 'https' in monitor:
        result['if'] = 'failed ' + _parse_http(monitor['https'])
    elif 'socket' in monitor:
        result['if'] = 'failed {}' 
    elif 'unix_socket' in monitor:
        result['if'] = 'failed unixsocket {0}'.format(repr(monitor['unix_socket']))
    elif 'max_cpu' in monitor:
        result['if'] = 'totalcpu usage > {0}'.format(repr(monitor['max_cpu']))
    elif 'max_memory' in monitor:
        result['if'] = 'totalmemory usage > {0}'.format(repr(monitor['max_memory']))
    elif 'max_processes' in monitor:
        result['if'] = 'children > {0}'.format(monitor['max_processes'])
    elif 'disk_used' in monitor:
        result['if'] = 'space > {0}'.format(monitor['disk_used'])
    elif 'file_changed' in monitor:    
        result['if'] = 'changed sha1 checksum'
        if 'checksum' in monitor:
            result['if'] += ' and expect the sum {0}'.format(monitor['checksum'])
    elif 'file_touched' in monitor:
        result['if'] = 'changed timestamp'
    if result:
        if monitor['cycles']:
            result['if'] += ' {0} cycles'.format(monitor['cycles'])
        result['then'] = action
    return result

def process(name, pidfile, start=None, stop=None, tries=None, alerts=(), restarts=(), execs=(), service=None, output_file=None):
    output_file = output_file or '/etc/monit/conf.d/{0}.conf'.format(name)
    service_cmd = __pillar__['packages'].get('service', '/usr/sbin/service')
    if not start:
        start = '{0} {1} start'.format(service_cmd, service or name)
    if not stop:
        stop = '{0} {1} stop'.format(service_cmd, service or name)
    rules = [
        dict(start=start),
        dict(stop=stop),
    ]
    
    for alert in alerts:
        rules.append(_parse(alert, 'alert'))
    
    for restart in restarts:
        rules.append(_parse(alert, 'restart'))
    
    if exe in execs:
        rules.append(_parse(exe, 'exec {0}'.format(exe['run'])))
    
    if tries:
        rules.append({'if': '{0} restarts in {0} cycles', 'then': 'alert and timeout'})
    
    process = dict(
        check='process',
        pidfile=pidfile,
        rules=rules,
    )
    _write_file(output_file, dict(checks=data))