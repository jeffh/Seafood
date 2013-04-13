environment:
    environment.set:
        - variables: {% if not pillar.get('environment', []) %}[]{% endif %}
            {% for k, v in pillar.get('environment', []).items() %}
            - '{{ k }}': '{{ v }}'
            {% endfor %}
