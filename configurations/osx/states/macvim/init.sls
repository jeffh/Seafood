{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

macvim:
    file.managed:
        - name: '{{ pkgs }}/MacVim.tbz'
        - source: https://macvim.googlecode.com/files/MacVim-snapshot-70-Mountain-Lion.tbz
        - source_hash: sha256=45cbd33534ae121424d5411900ac68e32aa2aa7b097257defcdab0c6066f571b
    cmd.script:
        - source: salt://macvim/scripts/install.sh
        - template: jinja
        - args: '/usr/local/bin/'
        - stateful: True
        - watch:
            - file: macvim
