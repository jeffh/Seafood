include:
    - java.core

java.jdk:
    package.installed:
        - name: openjdk-6-jdk
        - require:
            - package: java.core
