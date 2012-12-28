# fixed in develop branch: https://github.com/saltstack/salt/pull/1839
def set_special(user, special, cmd):
    "Sets a special cron job (a job that uses @-notation)."
    from salt.modules import cron
    cron.__salt__ = __salt__
    lst = __salt__['cron.list_tab'](user)
    for spec in lst['special']:
        if special == spec['spec'] and cmd == spec['cmd']:
            return 'present'
    spec = {'spec': special,
            'cmd': cmd}
    lst['special'].append(spec)
    comdat = cron._write_cron(user, cron._render_tab(lst))
    if comdat['retcode']:
        # Failed to commit, return the error
        return comdat['stderr']
    return 'new'

def absent(user, cmd):
    "Removes all cron jobs that run a given command (special or regular job)."
    from salt.modules import cron
    cron.__salt__ = __salt__
    lst = __salt__['cron.list_tab'](user)
    status = 'absent'
    for group in ('special', 'crons'):
        for spec in list(lst[group]):
            if special == spec['spec'] and cmd == spec['cmd']:
                lst[group].remove(spec)
                status = 'removed'
    comdat = cron._write_cron(user, cron._render_tab(lst))
    if comdat['retcode']:
        # Failed to commit, return the error
        return comdat['stderr']
    return status
