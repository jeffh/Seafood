{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

iterm:
    file.managed:
        - name: '{{ pkgs }}/iterm2.zip'
        - source: http://www.iterm2.com/downloads/stable/iTerm2_v1_0_0.zip
        - source_hash: sha256=2afad022b1e1f08b3ed40f0c2bde7bf7cce003852c83f85948c7f57a5578d9c5
    cmd.script:
        - source: salt://osx_base/scripts/zip_and_mv.sh
        - template: jinja2
        - args: 
            - iterm2.zip
            - iTerm.app
        - stateful: True
        - watch:
            - file: iterm
