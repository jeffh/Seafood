jenkins:
    package:
        - purged
    service.dead:
        - enabled: false
    environment.unset:
        - variables:
            - JENKINS_HOME
    user.present:
        - gid_from_name: True
        - require:
            - group: jenkins
    group:
        - present


'/home/jenkins':
    file.absent:
        - require:
            - service: jenkins
