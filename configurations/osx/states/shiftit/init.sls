{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}
include:
    - xquartz

shiftit:
    file.managed:
        - name: '{{ pkgs }}/shiftit.zip'
        - source: https://github.com/downloads/fikovnik/ShiftIt/ShiftIt-1.5.zip
        - source_hash: sha256=a00228a651f8ae61d06b1110e9a1db4358c1d4f9e05563397649b9cc8daca07d
    cmd.script:
        - source: salt://osx_base/scripts/unzip_and_mv.sh
        - template: jinja2
        - args: 
            - shiftit.zip
            - ShiftIt.app
        - stateful: True
        - watch:
            - file: shiftit
        - require:
            - cmd: xquartz
