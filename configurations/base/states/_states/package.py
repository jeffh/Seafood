import json

def _load_pkg():
    from salt.states import pkg
    pkg.__salt__ = __salt__
    pkg.__opts__ = __opts__
    pkg.__pillar__ = __pillar__
    pkg.__grains__ = __grains__
    return pkg

def installed(name, **kwargs):
    """Identical to pkg.installed, except parameters specified here
    can be overridden by pillar['packages'][name] data.
    """
    kwargs['name'] = name
    kwargs.update(__pillar__['packages'].get(name, {}))
    name = kwargs.pop('name')
    
    pkg = _load_pkg()

    if kwargs.get('version') == 'latest':
        kwargs.pop('version')
        return pkg.latest(name, **kwargs)
    else:
        return pkg.installed(name, **kwargs)


def purged(name, **kwargs):
    """Identical to pkg.purged, except parameters specified here
    can be overriden by pillar['packages'][name] data.
    """
    kwargs['name'] = name
    kwargs.update(__pillar__['packages'].get(name, {}))
    pkg = _load_pkg()
    return pkg.purged(kwargs['name'])
