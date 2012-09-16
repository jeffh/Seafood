# recommended installation is via get.rvm.io... which is a lot messier
rvm:
    cmd_alt.script:
        - unless: 'which rvm && rvm version | grep "^rvm 1.55"'
        - source: salt://rvm/get-rvm.sh

load_rvm:
    cmd.run:
        - unless: which rvm
        - name: source /usr/local/rvm/scripts/rvm || source .rvm/scripts/rvm
        - require:
            - cmd_alt: rvm