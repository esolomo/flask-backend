{% for data in zones %}
include "/etc/bind/named.conf.d/webfuturadmin/{{data.zone}}.conf";
{% endfor %}
