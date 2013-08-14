set_computer_name:
    cmd.run:
        - name: 'systemsetup -setcomputername {{ pillar['osx']['computer_name'] }}'
        - unless: 'systemsetup -getcomputername | grep -iq ": {{ pillar['osx']['computer_name'] }}"'
