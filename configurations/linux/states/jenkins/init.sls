jenkins:
    pkgrepo.managed:
    - humanname: Jenkins upstream package repository
    - name: deb http://pkg.jenkins-ci.org/debian binary/
    - key_url: http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key
    package:
        - installed
        - require:
            - pkgrepo: jenkins
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
