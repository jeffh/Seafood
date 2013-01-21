
def _set_variables(variables, path='/etc/environment'):
    env_vars = dict(__salt__['environment.read'](path))
    diff = dict((n, v) for n, v in variables.items() if n not in env_vars or env_vars[n] != v)
    env_vars.update(diff)
    
    if diff:
        __salt__['environment.write'](env_vars.items(), path)
    return diff


def _unset_variables(var_names, path='/etc/environment'):
    env_vars = dict(__salt__['environment.read'](path))
    diff = []
    for n in var_names:
        if n in env_vars:
            del env_vars[n]
            diff.append(n)
    
    if diff:
        __salt__['environment.write'](env_vars.items(), path)
    return diff


def set(name, variables, path='/etc/environment'):
    """Sets the list of variables to the given named path.
    
    name
        Does nothing. Simply for reference.
    variables
        A list of dictionaries or a dictionary of variables to set.
    path
        The file to write to. Defaults to /etc/environment
    """
    ret = {'changes': {},
           'comment': '{0}: Wrote to {1}'.format(name, path),
           'name': name,
           'result': True}

    # specified in list of dict form
    if not hasattr(variables, 'items'):
        newvariables = {}
        for d in variables:
            newvariables.update(d)
        variables = newvariables

    ret['changes'] = _set_variables(variables, path=path)
    return ret


def unset(name, variables, path='/etc/environment'):
    """Removed the list of variables to the given named path.
    
    name
        Does nothing. Simply for reference.
    variables
        A list of variables to unset.
    path
        The file to write to. Defaults to /etc/environment
    """
    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': True}

    variables = list(variables)
    ret['changes'] = _unset_variables(variables, path=path)
    if ret['changes']:
        ret['comment'] = '{0}: Wrote to {1}'.format(name, path)
    return ret