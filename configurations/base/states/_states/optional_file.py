"""
optional_files - handles the management of optional files.

This should be like the salt.states.file module, except that all its
operations have conditional-based execution.
"""
def _run_check(onlyif, unless, user, env):
    kwargs = {
        'runas': user,
        'env': env,
    }
    kwargs['env'] = kwargs['env'] or ()
    if onlyif:
        retcode = __salt__['cmd.retcode'](onlyif, **kwargs)
        if retcode != 0:
            return {'comment': 'onlyif exec failed (exit code=%s)' % retcode,
                    'changes': {},
                    'result': True}

    if unless:
        if __salt__['cmd.retcode'](unless, **kwargs) == 0:
            return {'comment': 'unless executed successfully',
                    'changes': {},
                    'result': True}

    return True

def managed(name, onlyif=None, unless=None, user=None, group=None, env=None, **kwargs):
    """Manages a given file. Defers to salt.states.file.managed.
    
    Only executes onlyif is satisfied or the unless is not satisfied.
    """
    user, env, group = kwargs.get('user'), kwargs.get('env'), kwargs.get('group')
    cret = _run_check(onlyif, unless, user, env)
    if isinstance(cret, dict):
        cret.update({'name': name})
        return cret

    from salt.states import file as f
    f.__salt__ = __salt__
    f.__opts__ = __opts__
    f.__pillar__ = __pillar__
    f.__grains__ = __grains__

    return f.managed(name, **kwargs)
