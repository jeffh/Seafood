http-ping:
    - name: example.afraid.org
      url: http://freedns.afraid.org/dynamic/update.php?some-random-key-is-here
      user: root    # default is root
      minute: '0'   # default is '*'
      hour: '*'     # default is '*'
      daymonth: '*' # default is '*'
      month: '*'    # default is '*'
      dayweek: '*'  # default is '*'
    - name: example2.afraid.org
      url: http://freedns.afraid.org/dynamic/update.php?some-other-random-key-is-here
      user: root    # default is root
      minute: '0'   # default is '*'
      hour: '*'     # default is '*'
      daymonth: '*' # default is '*'
      month: '*'    # default is '*'
      dayweek: '*'  # default is '*'