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
import csv
import json


def load_args():
    """Load command line arguments

    Return:
        parser - obj - returns the parser object
    """
    parser = argparse.ArgumentParser(
        description='Start grok pattern test.')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        choices=["stdout", "file", "both"],
        default="stdout",
        help=f"[stdout(default) | file | both]"
    )
    parser.add_argument(
        '-f',
        '--filename',
        help=f"Filename where output is written, required if "
             f"output option is set to file or both"
    )
    parser.add_argument(
        '-p',
        '--patterns',
        help=f"Filename of grok patterns"
    )
    parser.add_argument(
        '-e',
        '--events',
        help=f"Filename of event log to check patterns against"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-m',
        '--matches',
        action='store_true',
        default=True,
        help=f"outputs matches (default)"
    )

    return parser


def load_config(script_name):
    """Load the configuration file parameters

    Input:
        Name of the script. It is expected that the conf file is named after
        the script.
    Return:
        Config file as a hash.
    """
    path_etc = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etc")
    config = configparser.ConfigParser()
    config.sections()
    config.read(f'{path_etc}/{script_name}.conf')
    return config


def sql_query(time, service):
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
        f'WHERE time_stamp>={time} '\
        f"AND application_name=\'NAPLAN Online Service\'"

    return sql_query


def get_bsm_data(epoch_time):
    epoch_time_query = epoch_time-int(config['program']['timeframe'])

    api_query = f"https://{config['bsm']['hostname']}/topaz/gdeopenapi/GdeOpenApi"\
        f"?method=getData"\
        f"&user={config['bsm']['username']}"\
        f"&password={config['bsm']['password']}"\
        f"&query={sql_query(epoch_time_query, config['bsm']['service'])}"\
        f"&resultType=csv"

    api_result = requests.get(api_query)

    return api_result.text


"""body
"""
filename = os.path.basename(__file__).split('.')[0]
epoch_time = int(time.time())

# Import configurations
config = load_config(filename)

# load last sent file
last_file = f"{config['last_value']['path']}/{config['last_value']['file']}"

# Open last value file
try:
    last_values = open(last_file)
except FileNotFoundError:
    print('File does not exist')
    last_values = None

new_last_values = []
values_to_elastic = []

bsm_csv_data = get_bsm_data(epoch_time)
count = 0
csv_reader = csv.DictReader(bsm_csv_data.split("\n"), skipinitialspace=True)

for row in csv_reader:
    print(f"row count = {count}")
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
            print(f"{l_time.strip()} -- {row['EpochTime']} : {l_probe.strip()} -- {row['ProbeName']}")
            if l_probe.strip() == row['ProbeName'] and l_time.strip() == row['EpochTime']:
                new_last_values.append(f"{l_time},{l_probe}")
                found += 1
                print(f"found last val = {found}")
                break
        if found == 0:
            print(f"no value found = {found}")
            new_last_values.append(f"{row['EpochTime']},{row['ProbeName']}\n")
            values_to_elastic.append(row)




last_values.close()

try:
    f = open(last_file, mode='w')
    f.write(''.join(new_last_values))
except FileNotFoundError:
    print('File does not exist')


for i in values_to_elastic:
    print(f"{i['ProbeName']} - {i['EpochTime']})




# print(f"{bsm_csv_data}")


# Process the csv return data
# fieldnames = ("EpochTime","ApplicationName","TransactionName",
#               "AvgResponseTime","ProbeName","PerfCrit","PerfMinor",
#               "PerfOk","Status")
