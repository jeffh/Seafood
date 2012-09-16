coffeescript:
    cmd.run:
        - unless: which coffee
        - name: npm install -g coffee-script
        - require:
            - pkg: npm