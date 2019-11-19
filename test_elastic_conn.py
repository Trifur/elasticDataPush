from elasticsearch import Elasticsearch
from ssl import create_default_context

context = create_default_context(cafile="etc/cert.pem")
es = Elasticsearch(
    ['e7359svin2788.resourcestest.internal'],
    http_auth=('logstash_internal', 'Password42!'),
    scheme="https",
    port=9200,
    ssl_context=context,
)


    #   index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"

    #   cacert => "/etc/logstash/certs/elastic-stack-ca.crt"
    #   ssl => true
    #   ssl_certificate_verification => false