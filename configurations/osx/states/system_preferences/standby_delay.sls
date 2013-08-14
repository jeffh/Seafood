{% set standby_delay=salt['pillar.get']('osx:standby_delay', 4200) %}
standby_delay:
    # http://www.ewal.net/2012/09/09/slow-wake-for-macbook-pro-retina/
    # "Fixing" Slow Wake for MacBook Pro w/ Retina Display and MacBook Air
    cmd.run:
        - name: 'pmset -a standbydelay {{ standby_delay }}'
        - unless: '/usr/libexec/PlistBuddy /Library/Preferences/SystemConfiguration/com.apple.PowerManagement.plist -c "Print '':Custom Profile:AC Power:Standby Delay''" | grep -iq "^{{ standby_delay }}$"'
