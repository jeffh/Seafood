supervisor:
	package:
		- purged

'/etc/supervisor/':
    file:
    	- absent
