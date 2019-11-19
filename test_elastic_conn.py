from elasticsearch import Elasticsearch
from ssl import create_default_context
import os

path_etc = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etc")

context = create_default_context(cafile=f"{path_etc}/elastic-stack-ca.crt")
es = Elasticsearch(
    ['e7359svin2788.resourcestest.internal'],
    http_auth=('logstash_internal', 'Password42!'),
    scheme="https",
    port=9200,
    ssl_context=context,
)

print(es.info())

# result = es.get(index="_cluster")


    #   index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"

    #   cacert => "/etc/logstash/certs/elastic-stack-ca.crt"
    #   ssl => true
    #   ssl_certificate_verification => false