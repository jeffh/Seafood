{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

minecraft:
    file.managed:
        - name: '{{ pkgs }}/minecraft.dmg'
        - source: https://s3.amazonaws.com/Minecraft.Download/launcher/Minecraft.dmg
        - source_hash: sha256=654726af24a9a6b138b11ae426f3025621259211dd50abead7b0b2880fa9b0d8
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja
        - args: minecraft.dmg Minecraft.app
        - stateful: True
        - watch:
            - file: skype
