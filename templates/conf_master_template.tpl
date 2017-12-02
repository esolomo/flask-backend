{% for domain in managed_domains %}
zone "{{ domain }}" in {
	type master;
	file "{{ zone_file }}";
};
{% endfor %}
