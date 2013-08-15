{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}
{% set sha256hash='3f7c156fc4b13e3f0d0e44523ef2bd3cf7ea736126616dd2da28abb31840923c' %}
xquartz:

include:
    - osx_base

xquartz:
    file.managed:
        - name: '{{ pkgs }}/XQuartz.dmg'
        - source: http://xquartz.macosforge.org/downloads/SL/XQuartz-2.7.4.dmg
        - source_hash: sha256={{ sha256hash }}
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_install.sh
        - template: jinja2
        - args: 
            - XQuartz.dmg
            - XQuartz.pkg
            - '{{ sha256hash }}'
        - stateful: True
        - watch:
            - file: xquartz
