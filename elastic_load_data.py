#!/usr/bin/env python
# coding: utf-8
"""
Title           :elastic_load_data.py
Description     :Import data from BSM/APM to elasticsearch
Author          :Cyrill Illi
Date            :14/11/2019
Version         :0.1
Usage           :elastic_load_data.py -h
Notes           :See README.md and requirements.txt for more information
Python_version  :3.7.3
"""


import os.path
import configparser
import argparse
import sys
import requests
import time
import datetime
import csv
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, streaming_bulk
from ssl import create_default_context


def load_config(path_etc, script_name):
    """Load the configuration file parameters

    Input:
        Name of the script. It is expected that the conf file is named after
        the script.
    Return:
        Config file as a hash.
    """
    config = configparser.ConfigParser()
    config.sections()
    config.read(f'{path_etc}/{script_name}.conf')
    return config


def sql_query(from_time, to_time, service):
    sql_query = f'SELECT time_stamp AS EpochTime, '\
        f'application_name AS ApplicationName, '\
        f'szTransactionName AS TransactionName, '\
        f'AVG(dResponseTime) AS AvgResponseTime, '\
        f'szLocationName AS ProbeName, '\
        f'Tot_critical_Hits AS PerfCrit, '\
        f'Tot_minor_Hits AS PerfMinor, '\
        f'Tot_ok_Hits AS PerfOk, '\
        f'u_iStatus AS Status '\
        f'FROM trans_t '\
        f'WHERE time_stamp>={from_time} '\
        f'AND time_stamp<={to_time} '\
        f"AND application_name=\'NAPLAN Online Service\'"

    return sql_query


def get_bsm_data(epoch_time_query_from, epoch_time_query_to):
    """Connect to BSM and return probe raw data

    Input:
        epoch_time - date - current date in epoch time
        epoch_time_query - int - the number of seconds to look
    Return:
        Config file as a hash.
    """
    api_query = f"https://{config['bsm']['hostname']}/topaz/gdeopenapi/GdeOpenApi"\
        f"?method=getData"\
        f"&user={config['bsm']['username']}"\
        f"&password={config['bsm']['password']}"\
        f"&query={sql_query(epoch_time_query_from, epoch_time_query_to, config['bsm']['service'])}"\
        f"&resultType=csv"

    api_result = requests.get(api_query)

    return api_result.text


def gendata(values_to_elastic):
    for i in values_to_elastic:
        try:
            int(float(i['EpochTime']))
        except Exception as e:
            print(e)
        else:
            yield {
                "_index": 'bsm-data',
                "doc": {"type": "bpm",
                    "bsm.application.name": i['ApplicationName'],
                    "bsm.probe.name": i['ProbeName'],
                    "bsm.probe.status": i['Status'],
                    "bsm.probe.critical": i['PerfCrit'],
                    "bsm.probe.minor": i['PerfMinor'],
                    "bsm.probe.ok": i['PerfOk'],
                    "bsm.transaction.name": i['TransactionName'],
                    "bsm.transaction.response_time": i['AvgResponseTime'],
                    "bsm.transaction.time" : str(int(float(i['EpochTime']))),
                    "@timestamp": datetime.datetime.utcfromtimestamp(int(float(i['EpochTime'])))
                }
            }


def open_es():
    context = create_default_context(
        cafile=f"{path_etc}/{config['elastic']['ca_cert']}")
    es = Elasticsearch(
        [config['elastic']['hostname']],
        http_auth=(config['elastic']['username'], config['elastic']['password']),
        scheme=config['elastic']['scheme'],
        port=config['elastic']['port'],
        ssl_context=context,
    )
    return es


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


"""body
"""
path_etc = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etc")
filename = os.path.basename(__file__).split('.')[0]
epoch_time = int(time.time())

# Import configurations
config = load_config(path_etc, filename)

# load last sent file
last_file = f"{config['last_value']['path']}/{config['last_value']['file']}"



timeframe = int(config['program']['timeframe'])

while timeframe > 0:
    print(f"Timeframe = {timeframe}")
    epoch_time_query_from = epoch_time-timeframe
    epoch_time_query_to = epoch_time_query_from+500000
    bsm_csv_data = get_bsm_data(epoch_time_query_from, epoch_time_query_to)
    csv_reader = csv.DictReader(bsm_csv_data.split("\n"), skipinitialspace=True)

    # Open last value file
    try:
        last_values = open(last_file)
    except FileNotFoundError:
        print('File does not exist')
        last_values = None

    new_last_values = []
    values_to_elastic = []
    count = 0
    for row in csv_reader:
        nr_elements = len(list(row))
        if nr_elements == 1 or "Returned 10000" in row['EpochTime'] or row['EpochTime'] is None:
            print(row)
            continue
        count += 1
        if last_values is None or os.stat(last_file).st_size == 0:
            new_last_values.append(f"{row['EpochTime']},{row['ProbeName']}\n")
            values_to_elastic.append(row)
        else:
            found = 0
            for l_val in last_values:
                if not l_val:
                    continue
                l_time, l_probe = l_val.split(',')
                # print(f"{l_time.strip()} -- {row['EpochTime']} : {l_probe.strip()} -- {row['ProbeName']}")
                if l_probe.strip() == row['ProbeName'] and l_time.strip() == row['EpochTime']:
                    new_last_values.append(f"{l_time},{l_probe}")
                    found += 1
                    # print(f"found last val = {found}")
                    break
            if found == 0:
                # print(f"no value found = {found}")
                new_last_values.append(f"{row['EpochTime']},{row['ProbeName']}\n")
                values_to_elastic.append(row)

    last_values.close()

    # write values to last value file
    try:
        f = open(last_file, mode='w')
        f.write(''.join(new_last_values))
        f.close()
    except FileNotFoundError:
        print('File does not exist')

    # Push data to elasticsearch
    es = open_es()

    for i in values_to_elastic:
        try:
            int(float(i['EpochTime']))
        except Exception as e:
            print(e)
        else:
            status_ok = 0
            status_nok = 0
            if "0" in i['Status']:
                status_ok = 1
            else:
                status_nok = 1

            try:
                es.index(index='bsm-data',
                    body={"type": "bpm",
                    "bsm.application.name": i['ApplicationName'],
                    "bsm.probe.name": i['ProbeName'],
                    "bsm.probe.status": i['Status'],
                    "bsm.probe.status_ok": status_ok,
                    "bsm.probe.status_nok": status_nok,
                    "bsm.probe.critical": i['PerfCrit'],
                    "bsm.probe.minor": i['PerfMinor'],
                    "bsm.probe.ok": i['PerfOk'],
                    "bsm.transaction.name": i['TransactionName'],
                    "bsm.transaction.response_time": i['AvgResponseTime'],
                    "bsm.transaction.time" : str(int(float(i['EpochTime']))),
                    "@timestamp": datetime.datetime.utcfromtimestamp(int(float(i['EpochTime'])))
                    }
                )
                es.indices.refresh(index='bsm-data')
            except Exception as e:
                print(e)

    timeframe -= 500000



