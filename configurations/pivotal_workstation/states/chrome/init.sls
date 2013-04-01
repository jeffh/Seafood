{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

chrome:
    file.managed:
        - name: '{{ pkg }}/chrome.dmg'
        - source: https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg
        - source_hash: sha256=7d47070fdaa92eb641fa688cf4e2cf7e28cc9f05e02ed81e834388516b28b28a
    cmd.wait:
        - name: "{{ scripts }}/dmg_and_cp.sh '{{ pkgs }}/chrome.dmg' 'Google Chrome.app' '/Applications/Google Chrome.app'"
        - stateful: True
        - watch:
            - file: '{{ pkgs }}/chrome.dmg'
