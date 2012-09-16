# Bug fixes / tinkering to the salt's cmd module

'''
Execution of arbitrary commands.
================================

The cmd state module manages the enforcement of executed commands, this
state can tell a command to run under certain circumstances.

Available Functions
-------------------

The cmd state only has a single function, the ``run`` function

run
    Execute a command given certain conditions

    A simple example:

    .. code-block:: yaml

        date > /tmp/salt-run:
        cmd:
            - run

Only run if another execution returns successfully, in this case truncate
syslog if there is no disk space:

.. code-block:: yaml

    > /var/log/messages:
      cmd.run:
        - unless: echo 'foo' > /tmp/.test
'''

# Import python libs
import grp
import os
import copy

# Import salt libs
from salt.exceptions import CommandExecutionError
import salt.utils.templates


def _run_check(cmd_kwargs, ifonly, unless, cwd, user, group, shell):
    '''
    Execute the ifonly logic and return data if the ifonly fails
    '''
    ret = {}

    if group:
        try:
            egid = grp.getgrnam(group).gr_gid
            if not __opts__['test']:
                os.setegid(egid)
        except KeyError:
            ret['comment'] = 'The group {0} is not available'.format(group)
            return {'comment': 'The group {0} is not available'.format(group),
                    'result': False}

    # TODO: FIXME
    kwargs = copy.deepcopy(cmd_kwargs)
    allowed_kwargs = set(['cwd', 'runas', 'shell'])
    for key in cmd_kwargs.keys():
        if key not in allowed_kwargs:
            del kwargs[key]
    allowed_kwargs = cmd_kwargs.pop('env', None) or ()

    if ifonly:
        if __salt__['cmd.retcode'](ifonly, **kwargs) != 0:
            ret['comment'] = 'ifonly exec failed'
            ret['result'] = True
            return {'comment': 'ifonly exec failed',
                    'result': True}

    if unless:
        if __salt__['cmd.retcode'](unless, **kwargs) == 0:
            return {'comment': 'unless executed successfully',
                    'result': True}
    # No reason to stop, return True
    return True


def wait(name,
        ifonly=None,
        unless=None,
        cwd='/root',
        user=None,
        group=None,
        shell=None):
    '''
    Run the given command only if the watch statement calls it

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    ifonly
        A command to run as a check, run the named command only if the command
        passed to the ``ifonly`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    user
        The user name to run the command as

    group
        The group context to run the command as

    shell
        The shell to use for execution, defaults to /bin/sh
    '''
    return {'name': name,
            'changes': {},
            'result': True,
            'comment': ''}


def wait_script(name,
        source=None,
        template=None,
        ifonly=None,
        unless=None,
        cwd='/root',
        user=None,
        group=None,
        shell=None,
        env=None,
        **kwargs):
    '''
    Download a script from a remote source and execute it only if a watch
    statement calls it.

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    ifonly
        A command to run as a check, run the named command only if the command
        passed to the ``ifonly`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    user
        The user name to run the command as

    group
        The group context to run the command as

    shell
        The shell to use for execution, defaults to the shell grain
    '''
    return {'name': name,
            'changes': {},
            'result': True,
            'comment': ''}


def run(name,
        ifonly=None,
        unless=None,
        cwd='/root',
        user=None,
        group=None,
        shell=None,
        env=(),
        **kwargs):
    '''
    Run a command if certain circumstances are met

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    ifonly
        A command to run as a check, run the named command only if the command
        passed to the ``ifonly`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    user
        The user name to run the command as

    group
        The group context to run the command as

    shell
        The shell to use for execution, defaults to the shell grain
    '''
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not os.path.isdir(cwd):
        ret['comment'] = 'Desired working directory is not available'
        return ret

    if env:
        _env = {}
        for var in env.split():
            try:
                k, v = var.split('=')
                _env[k] = v
            except ValueError:
                ret['comment'] = 'Invalid enviromental var: "{0}"'.format(var)
                return ret
        env = _env

    pgid = os.getegid()

    cmd_kwargs = {'cwd': cwd,
                  'runas': user,
                  'shell': shell or __grains__['shell'],
                  'env': env}

    try:
        cret = _run_check(cmd_kwargs, ifonly, unless, cwd, user, group, shell)
        if isinstance(cret, dict):
            ret.update(cret)
            return ret

        # Wow, we passed the test, run this sucker!
        if not __opts__['test']:
            try:
                cmd_all = __salt__['cmd.run_all'](name, **cmd_kwargs)
            except CommandExecutionError as e:
                ret['comment'] = str(e)
                return ret

            ret['changes'] = cmd_all
            ret['result'] = not bool(cmd_all['retcode'])
            ret['comment'] = 'Command "{0}" run'.format(name)
            return ret
        ret['result'] = None
        ret['comment'] = 'Command "{0}" would have been executed'.format(name)
        return ret

    finally:
        os.setegid(pgid)


def script(name,
        source=None,
        template=None,
        ifonly=None,
        unless=None,
        cwd='/root',
        user=None,
        group=None,
        shell=None,
        env=None,
        **kwargs):
    '''
    Download a script from a remote source and execute it. The name can be the
    source or the source value can be defined.

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    ifonly
        A command to run as a check, run the named command only if the command
        passed to the ``ifonly`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    user
        The user name to run the command as

    group
        The group context to run the command as

    shell
        The shell to use for execution, defaults to the shell grain
    '''
    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': False}

    if not os.path.isdir(cwd):
        ret['comment'] = 'Desired working directory is not available'
        return ret

    if env is None:
        env = kwargs.get('__env__', 'base')

    pgid = os.getegid()

    cmd_kwargs = copy.deepcopy(kwargs)
    cmd_kwargs.update({'cwd': cwd,
                  'runas': user,
                  'shell': shell or __grains__['shell'],
                  'env': env,
                  'user': user,
                  'group': group,
                  'cwd': cwd,
                  'template': template})

    # Changet the source to be the name arg if it is nto specified
    if source is None:
        source = name

    try:
        cret = _run_check(cmd_kwargs, ifonly, unless, cwd, user, group, shell)
        if isinstance(cret, dict):
            ret.update(cret)
            return ret

        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Command "{0}" would have been executed'
            ret['comment'] = ret['comment'].format(name)
            return ret

        # Wow, we passed the test, run this sucker!
        try:
            cmd_all = __salt__['cmd.script'](source, **cmd_kwargs)
        except CommandExecutionError as e:
            ret['comment'] = str(e)
            return ret

        ret['changes'] = cmd_all
        if kwargs.get('retcode', False):
            ret['result'] = not bool(cmd_all)
        else:
            ret['result'] = not bool(cmd_all['retcode'])
        ret['comment'] = 'Command "{0}" run'.format(name)
        return ret

    finally:
        os.setegid(pgid)

def mod_watch(name, **kwargs):
    '''
    Execute a cmd function based on a watch call
    '''
    if kwargs['sfun'] == 'wait' or kwargs['sfun'] == 'run':
        return run(name, **kwargs)
    elif kwargs['sfun'] == 'wait_script' or kwargs['sfun'] == 'script':
        return script(name, **kwargs)