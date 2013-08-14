set_computer_sleep:
    cmd.run:
        - name: 'systemsetup -setcomputersleep {{ pillar['osx']['power_management']['computer_sleep'] }}'
        - unless: 'systemsetup -getcomputersleep | grep -iq "{{ pillar['osx']['power_management']['computer_sleep'] }} minute"'
