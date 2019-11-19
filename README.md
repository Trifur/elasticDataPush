# Elastic Data Pusher

This program is desigend to push data to an elasticsearch instance.

## Setup

### Tested with

- Python >= 3.7.x

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

Index name = bsm_probe_data

('EpochTime', '1.5738055E9'),
('ApplicationName', 'NAPLAN Online Service'),
('TransactionName', '01_NAPLAN_Launch_Test'),
('AvgResponseTime', '115189.0'),
('ProbeName', 'MeredinNAPLANBPM'),
('PerfCrit', '0'),
('PerfMinor', '0'),
('PerfOk', '0'),
('Status', '1')

time - convert to long and then to @timestamp

type - probe
bsm.application.name - keyword
bsm.tansaction.name - keyword
bsm.transaction.time - long
bsm.transaction.response.time - float
bsm.probe.name - keyword
bsm.probe.performance.critical - short
bsm.probe.performance.minor - short
bsm.probe.performance.ok - short
bsm.probe.status - short

    var serviceHealth = Math.round((nrOfProbes / nrOfApiProbes) * 100);

    // nrOfApiProbes    ;   Number of probes allocated to the service, returned by the API
    // nrOfProbes       ;   Number of probes that have data, returned by the API
    // nrOfNonProbes    ;   Number of probes that do not have data (nrOfApiProbes - nrOfProbes)

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