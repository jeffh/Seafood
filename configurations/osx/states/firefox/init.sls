{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

firefox:
    file.managed:
        - name: '{{ pkgs }}/firefox.dmg'
        - source: https://download.mozilla.org/?product=firefox-23.0&os=osx&lang=en-US
        - source_hash: sha256=4406cb7522c673bc400b14ea30234b434671d61fa4775d7f6405cfcebe333f4e
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja2
        - args: 
            - firefox.dmg
            - Firefox.app
        - stateful: True
        - watch:
            - file: firefox
