{% for domain in managed_domains %}
zone "{{ domain }}" in {
	type slave;
	masters {  {{ primary_ns_ip_ipv4 }}; {{ primary_ns_ip_ipv6 }}; };
	file "{{ zone_file }}";
};
{% endfor %}
