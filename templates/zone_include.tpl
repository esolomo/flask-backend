{% for data in zones %}
include "{{ config_dir }}/{{data.zone}}.conf";
{% endfor %}
