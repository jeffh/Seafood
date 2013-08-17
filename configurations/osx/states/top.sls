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
        - 1password.absent
        - alfred.absent
        - caffeine.absent
        - ccmenu.absent
        - chrome.absent
        - firefox.absent
        - dropbox.absent
        - iterm.absent
        - shiftit.absent
        - macvim.absent
        - system_preferences.remote_desktop
        - system_preferences.remote_login
        - system_preferences.power_management
        - system_preferences.standby_delay
