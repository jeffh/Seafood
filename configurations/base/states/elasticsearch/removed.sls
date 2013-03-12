elasticsearch:
	package:
		- purged

'/etc/elasticsearch/elasticsearch.yml':
	file:
		- absent

'/etc/elasticsearch/logging.yml':
	file:
		- absent
