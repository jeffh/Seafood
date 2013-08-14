monit:
    package:
        - purged

'/etc/monit/':
    file:
    	- absent
