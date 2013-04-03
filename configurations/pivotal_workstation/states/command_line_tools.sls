{% set scripts=pillar['caches']['scripts'] %}
{% set tmp=pillar['caches']['tmp'] %}

command_line_tools:
    file.managed:
        - name: '{{ tmp }}/xcode_cltools.dmg'
        - source: salt://external_files/xcode/xcode461_cltools_10_86938245a.dmg
    cmd.wait:
        - name: '{{ scripts }}/dmg_and_install.sh {{ tmp }}/xcode_cltools.dmg "Command Line Tools (Mountain Lion).mpkg"'
        - stateful: True
        - watch:
            - file: '{{ pkgs }}/xcode_cltools.dmg'
