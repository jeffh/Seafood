set_display_sleep:
    cmd.run:
        - name: 'systemsetup -setdisplaysleep {{ pillar['osx']['power_management']['display_sleep'] }}'
        - unless: 'systemsetup -getdisplaysleep | grep -iq "{{ pillar['osx']['power_management']['display_sleep'] }} minute"'
