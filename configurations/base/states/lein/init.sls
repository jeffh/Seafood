include:
    - directories

lein:
    file.managed:
        - name: /usr/local/bin/lein
        - mode: 755
        - source: 'https://raw.github.com/technomancy/leiningen/stable/bin/lein'
        - source_hash: sha256=2bc7cf2b07950ca7dcb0a4c93ed9844924452ce6a12cd40e9358cadc93547899
        - require:
            - file: /usr/local/bin/
