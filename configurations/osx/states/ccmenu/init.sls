{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

ccmenu:
    file.managed:
        - name: '{{ pkgs }}/ccmenu.dmg'
        - source: 'http://downloads.sourceforge.net/project/ccmenu/CCMenu/1.5/ccmenu-1.5-b.dmg?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fccmenu%2Ffiles%2FCCMenu%2F&ts=1364619310'
        - source_hash: sha256=7cbdc6b3ff477fe420ab121e0892e0aebc48b1a9620aacfb6324932900d6b6cc
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja
        - args: ccmenu.dmg CCMenu.app
        - stateful: True
        - watch:
            - file: chrome
