golang:
    package:
        - purged
    environment.unset:
        - variables:
            - GOARM
            - GOOS
            - GOARCH
            - GOROOT

'/usr/local/go/':
    file:
        - absent