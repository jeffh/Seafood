include:
    - java.jdk
    - java.core

java:
    package.installed:
        - name: openjdk-6-jre
        - require:
            - package: java.jdk
            - package: java.core
