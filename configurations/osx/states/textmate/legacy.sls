{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

textmate:
    file.managed:
        - name: '{{ pkgs }}/textmate1.zip'
        - source: http://archive.textmate.org/TextMate_1.5.11_r1635.zip
        - source_hash: sha256=33897ffcc743db6a9ac4bac7f440f9feb94e57aa788755b46eab37cf9c6efb6c
    cmd.script:
        - source: salt://osx_base/scripts/unzip_and_mv.sh
        - template: jinja
        - args: textmate1.zip 'TextMate.app'
        - stateful: True
        - watch:
            - file: textmate
