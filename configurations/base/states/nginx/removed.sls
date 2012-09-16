nginx:
    pkg:
        - purged
    service.dead:
        - enabled: false

'/usr/share/nginx/www/':
    file:
        - absent
        
'/etc/nginx/':
    file:
        - absent