{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

skype:
    file.managed:
        - name: '{{ pkgs }}/skype.dmg'
        - source: http://www.skype.com/go/getskype-macosx.dmg
        - source_hash: sha256=cc549d8dfccd5f056917500cb7bfadaffe4db536c14cab2c0c5c6e9c1f2abefc
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja
        - args: skype.dmg Skype.app
        - stateful: True
        - watch:
            - file: skype
