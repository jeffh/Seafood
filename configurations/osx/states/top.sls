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
        - firefox
        - dropbox
        - iterm
        - shiftit
        - macvim
        - system_preferences.remote_desktop
        - system_preferences.remote_login
        - system_preferences.power_management
        - system_preferences.standby_delay
