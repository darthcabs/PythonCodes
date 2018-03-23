#!/usr/bin/env python3.6

from datetime import date, timedelta
from datetime import datetime

import sys
import boto3

try:
    end = str(datetime.strptime(sys.argv[4], '%Y-%m-%d').date())
    start = str(datetime.strptime(sys.argv[3], '%Y-%m-%d').date())
    tagKey = sys.argv[1]
    tagValue = sys.argv[2]
except IndexError:
    print('Usage: billing.py <tag_key> <tag_value> <start_date> <end_date>')
    print('Date format: yyyy-mm-dd')
    sys.exit(0)

ce = boto3.client('ce')

costs = ce.get_cost_and_usage(
    TimePeriod={
        'Start': start,
        'End': end
    },
    Granularity='MONTHLY',
    Filter={
        'Tags': {
            'Key': tagKey,
            'Values': [
                tagValue
            ]
        }
    },
    Metrics=[
        "UnblendedCost",
        "UsageQuantity"
    ],
    GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'SERVICE'
        }
    ]
)

#print(costs)

print('Costs associated to tag ' + tagKey + '=' + tagValue + ', by month:\n')
for month in costs['ResultsByTime']:
    mes = datetime.strptime(month['TimePeriod']['Start'],'%Y-%m-%d').strftime('%b %Y')
    for srv in month['Groups']:
        print('\t' + mes + ': ' + '\t' +
              srv['Metrics']['UnblendedCost']['Unit'] + ' ' + 
              str(round(float(srv['Metrics']['UnblendedCost']['Amount']), 2)) + '\t' +
              srv['Keys'][0])
    print()