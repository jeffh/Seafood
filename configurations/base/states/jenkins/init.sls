jenkins:
    package:
        - installed
    service.running:
        - watch:
            - package: jenkins
            - environment: jenkins
            - user: jenkins
            - group: jenkins
    environment.set:
        - variables:
            - JENKINS_HOME: /home/jenkins
    user.present:
        - name: jenkins
        - home: /home/jenkins/
        - gid_from_name: True
        - require:
            - group: jenkins
    group.present:
        - name: jenkins
