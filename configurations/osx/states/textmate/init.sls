{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

textmate:
    file.managed:
        - name: '{{ pkgs }}/textmate2.tbz'
        - source: https://api.textmate.org/downloads/release
        - source_hash: sha256=89113b5d0df61d868c9cadcaf7e4f6557e6c971eb2ee209d73625a9b28525d6d
    cmd.script:
        - source: salt://osx_base/scripts/bunzip_and_mv.sh
        - template: jinja
        - args: textmate2.tbz 'TextMate.app'
        - stateful: True
        - watch:
            - file: textmate
