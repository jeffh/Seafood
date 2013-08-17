{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

alfred:
    file.managed:
        - name: '{{ pkgs }}/alfred.zip'
        - source: http://cachefly.alfredapp.com/Alfred_2.0.2_178.zip
        - source_hash: sha256=1b45d5205a5837fc589d6b3b02d8ba3e5e3ccff88dd6e715933751de96c0b600
        - backup: False
    cmd.script:
        - source: salt://osx_base/scripts/unzip_and_mv.sh
        - template: jinja
        - args: "alfred.zip 'Afred 2.app'"
        - stateful: True
        - watch:
            - file: alfred
