base:
    '*':
        #- users
        - salt.minion
        - osx_base
    'roles:salt-master':
        - match: grain
        - salt.master
    'roles:desktop':
        - match: grain
        - 1password
        - alfred
        - caffeine
        - ccmenu
        - chrome
        - dropbox
        - system_preferences.remote_login
        - system_preferences.power_management
        - system_preferences.standby_delay
