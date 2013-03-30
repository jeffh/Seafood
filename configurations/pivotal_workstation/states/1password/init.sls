{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

1Password:
    file.managed:
        - source: salt://external_files/1password/1password-3.8.20.zip
        - source_hash: sha256=56aef138f06fc92d641c424742bc40887cd19e6029f20409ec06ad5514b8cff1
        - backup: False
    cmd.wait:
        - name: '{{ scripts }}/unzip_and_mv.sh 1Password /Applications/1Password.app'
        - watch:
            - file: '{{ pkgs }}/1password.zip'

1password:
    cmd.wait:
        - name: '{{ scripts }}/unzip_and_mv.sh {{ pkgs }}/1password.zip 1Password.app /Applications/1Password.app'
        - stateful: True
        - watch:
            - file: '{{ pkgs }}/1password.zip'
