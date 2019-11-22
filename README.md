# Elastic Data Pusher

This program is desigend to push data to an elasticsearch instance.

## Setup

### Tested with

- Python >= 3.6.x

### **Setup virtual python development environment**

```bash
$ git clone <repo>
$ cd elasticDataPush
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements
```

### SSL

If you are using anaconda install the openssl package:

```bash
conda install -c anaconda openssl
```

On linux openssla should be installed as part of the default OS install.

## Elasticsearch Index

Index name = bsm-data

The following is the index creation definition in json.  It is used for the ingestion of bsm data,

```json
PUT /bsm-data
{
  "settings" : {
    "number_of_shards" : 1,
    "number_of_replicas" : 0
  },
  "mappings" : {
    "properties": {
      "type": { "type": "keyword" },
      "@timestamp": { "type": "date" },
      "bsm": {
        "properties": {
          "application": {
            "properties": {
              "name": { "type": "keyword" }
            }
          },
          "probe": {
            "properties": {
              "name": { "type": "keyword" },
              "status": { "type": "short" },
              "status_ok": { "type": "short" },
              "status_nok": { "type": "short" },
              "critical": { "type": "short" },
              "minor": { "type": "short" },
              "ok": { "type": "short" }
            }
          },
          "transaction": {
            "properties" : {
              "name": { "type": "keyword" },
              "epochtime": { "type": "text" },
              "response_time": { "type": "float" }
            }
          }
        }
      }
    }
  }
}
```

## Dashboards

From Kibana->Management->Saved Objects
Run import and select the json file located under the dashboard directory. Thsi will create the index pattern, visualizations, and the dashboard.