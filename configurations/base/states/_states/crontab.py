# needs to be merged into salt's cron when possible

def _check_cron(name, user, special):
    for rule in __salt__['cron.list_tab'](user).get('special', []):
        if rule['cmd'] == name:
            if rule['spec'] == special:
                return 'present'
            return 'update'
    return 'absent'

def absent(name, user='root'):
    ret = {
        'changes': {},
        'comment': '',
        'name': name,
        'result': True,
    }

    if __opts__['test']:
        status = _check_cron(name, user, special)
        ret['result'] = None
        if status == 'absent':
            ret['comment'] = 'Cron {0} is absent'.format(name)
        elif status == ('removed', 'updated'):
            ret['result'] = True
            ret['comment'] = 'Cron {0} is set to be removed'.format(name)
        return ret

    data = __salt__['crontab.remove'](user, name)
    if data == 'absent':
        ret['comment'] = 'Cron {0} is already absent'.format(name)
        return ret

    if data == 'removed':
        ret['comment'] = 'Cron {0} removed from {1}\'s crontab'.format(name, user)
        ret['changes'] = {user: name}
        return ret

    ret['comment'] = ('Cron {0} for user {1} failed to commit with error \n{2}'
                      .format(name, user, data))
    ret['result'] = False
    return ret

def special(name, user='root', special='@reboot'):
    ret = {
        'changes': {},
        'comment': '',
        'name': name,
        'result': True,
    }

    if __opts__['test']:
        status = _check_cron(name, user, special)
        ret['result'] = None
        if status == 'absent':
            ret['comment'] = 'Cron {0} is set to be added'.format(name)
        elif status == 'present':
            ret['result'] = True
            ret['comment'] = 'Cron {0} already present'.format(name)
        elif status == 'update':
            ret['comment'] = 'Cron {0} is set to be updated'.format(name)
        return ret

    data = __salt__['crontab.set_special'](user, special, name)
    if data == 'present':
        ret['comment'] = 'Cron {0} already present'.format(name)
        return ret

    if data == 'new':
        ret['comment'] = 'Cron {0} added to {1}\'s crontab'.format(name, user)
        ret['changes'] = {user: name}
        return ret

    if data == 'updated':
        ret['comment'] = 'Cron {0} updated'.format(name, user)
        ret['changes'] = {user: name}
        return ret
    ret['comment'] = ('Cron {0} for user {1} failed to commit with error \n{2}'
                      .format(name, user, data))
    ret['result'] = False
    return ret
