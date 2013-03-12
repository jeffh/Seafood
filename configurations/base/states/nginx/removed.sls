nginx:
    pkg:
        - purged
    service.dead:
        - enabled: false
    user.absent:
    	- name: www-data
    group.absent:
    	- name: www-data

'/usr/share/nginx/www/':
    file:
        - absent
        
'/etc/nginx/':
    file:
        - absent
