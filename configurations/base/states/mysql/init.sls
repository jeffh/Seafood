mysql:
    pkg.installed:
        - name: mysql
    service.ensure:
        - name: mysql
