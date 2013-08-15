{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

dropbox:
    file.managed:
        - name: '{{ pkgs }}/dropbox.dmg'
        - source: https://www.dropbox.com/download?plat=mac
        - source_hash: sha256=3ddf14f8a531ed292dcd79589117825bbfb51c5eea33144c46660c460f77bd76
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja2
        - args: 
            - dropbox.dmg
            - Dropbox.app
        - stateful: True
        - watch:
            - file: dropbox
