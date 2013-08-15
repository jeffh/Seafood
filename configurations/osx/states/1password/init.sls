{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

include:
    - osx_base

1password:
    file.managed:
        - name: {{ pkgs }}/1password.zip
        - source: https://d13itkw33a7sus.cloudfront.net/dist/1P/mac/1Password-3.8.20.zip
        - source_hash: sha256=56aef138f06fc92d641c424742bc40887cd19e6029f20409ec06ad5514b8cff1
        - backup: False
    cmd.script:
        - source: salt://osx_base/scripts/unzip_and_mv.sh
        - template: jinja2
        - args: 
            - 1password.zip
            - 1Password.app
        - stateful: True
        - watch:
            - file: 1password
