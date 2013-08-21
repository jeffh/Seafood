include:
    - python

pip:
    {% if grains['os'] != 'MacOS' %}
    package.installed:
        - name: python-pip
        - require:
            - package: python
    {% endif %}
