{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

caffeine:
    file.managed:
        - name: {{ pkgs }}/caffeine.zip
        - source: http://download.lightheadsw.com/download.php?software=caffeine
        - source_hash: sha256=9203c30951f9aab41ac294bbeb1dcef7bed401ff0b353dcb34d68af32ea51853
        - backup: False
    cmd.script:
        - source: salt://osx_base/scripts/unzip_and_mv.sh
        - template: jinja
        - args: "caffeine.zip 'Caffeine 2.app'"
        - stateful: True
        - watch:
            - file: caffeine
