# Elastic Data Pusher

This program is desigend to push data to an elasticsearch instance.

## Table of Contents


- [Elastic Data Pusher](#elastic-data-pusher)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
    - [Requirements](#requirements)
    - [**Setup virtual python development environment**](#setup-virtual-python-development-environment)
    - [SSL](#ssl)
  - [Elasticsearch Index](#elasticsearch-index)
  - [Dashboards](#dashboards)
  - [Contributors](#contributors)

## Setup

### Requirements

- Python >= 3.6.x

For modules see the requirements.txt file

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

On linux openssl is installed as part of the default OS install.

## Elasticsearch Index

Index name = bsm-data

The following is the index creation definition in json.  It is used for the ingestion of bsm data.

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

From Kibana -> Management -> Saved Objects

Run import and select the json file located under the dashboard directory. This will create the index pattern, visualizations, and the dashboard.

## Contributors

- Cyrill Illi (cyrill.illi@kineticit.com.au)