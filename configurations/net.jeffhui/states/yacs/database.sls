include:
    - postgresql

yacs_database:
    postgres_user.present:
        - password: {{ pillar['passwords']['yacs_db'] }}
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
    postgres_database.present:
        - owner: yacs
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
            - postgres_user: yacs
