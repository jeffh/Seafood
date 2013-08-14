{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

chrome:
    file.managed:
        - name: '{{ pkgs }}/chrome.dmg'
        - source: https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg
        - source_hash: sha256=56e72b8c4a0862c8349c892054be68220b67202e348d46cdb8875dc88caf06a0
    cmd.script:
        - source: salt://osx_base/scripts/dmg_and_cp.sh
        - template: jinja2
        - args: 
            - chrome.dmg
            - Google Chrome.app
        - stateful: True
        - watch:
            - file: chrome
