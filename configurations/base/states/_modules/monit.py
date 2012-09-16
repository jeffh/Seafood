# TODO: incomplete. only supports reading of monit config files
# need to support writing to /etc/monit/conf.d/*.conf
import os
import re
import logging
from collections import defaultdict

from salt.modules.service import grainmap

# for monit, if is a noise keyword
# but parsing will be easier for use if we parse 'if's
NOISE_KEYWORDS = set('and with within has using use on only usage program programs'.split(' '))
ENTRY_KEYWORDS = set('if else group depends start stop'.split(' '))
start_keywords = set(['set', 'check', 'include'])

logger = logging.getLogger(__name__)


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
    return '\n'.join('{name} {action} {extra}'.format(**d(action)) for action in actions)
    
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

def check_process(name, pidfile, start=None, stop=None):
    config_filepath = '/etc/monit/conf.d/{0}.conf'.format(name)
    if not start:
        start = os.path.join(grainmap(__grains__['os']), name)
    if not stop:
        stop = os.path.join(grainmap(__grains__['os']), name)
    process = {
        'check': 'process',
        'pidfile': pidfile,
        'rules': [
            dict(start=start),
            dict(stop=stop),
        ],
    }
    _write_file(config_filepath, data)