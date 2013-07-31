include:
    - postgresql

yacs_database:
    postgres_user.present:
        - name: yacs
        - password: {{ pillar['passwords']['yacs_db'] }}
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
    postgres_database.present:
        - name: yacs
        - owner: yacs
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
            - postgres_user: yacs_database
