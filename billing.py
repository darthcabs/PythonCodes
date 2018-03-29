def lambda_handler(event, context):
    from datetime import datetime
    import boto3

    try:
        end = str(datetime.strptime(event['enddate'], '%Y-%m-%d').date())
        start = str(datetime.strptime(event['startdate'], '%Y-%m-%d').date())
        tagKey = event['tagkey']
        tagValue = event['tagvalue']
    except IndexError:
        return 'Required params: tagkey: str, tagvalue: str, startdate: str, enddate: str. Date format: yyyy-mm-dd'

    ce = boto3.client('ce')

    costs = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end
        },
        Granularity='DAILY',
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

    result = list()

    for entry in costs['ResultsByTime']:
        day = {}
        if not entry['Groups']:
            day['Date'] = datetime.strptime(entry['TimePeriod']['Start'],'%Y-%m-%d').strftime('%d/%m/%Y')
            day['Services'] = []
            service = {}
            service['Name'] = '-'
            service['Cost'] = 0.00
            service['Currency'] = 'USD'
            day['Services'].append(service)
            result.append(day)
        else:
            day['Date'] = datetime.strptime(entry['TimePeriod']['Start'],'%Y-%m-%d').strftime('%d/%m/%Y')
            day['Services'] = []
            for subentry in entry['Groups']:
                service = {}
                service['Name'] = subentry['Keys'][0]
                service['Cost'] = subentry['Metrics']['UnblendedCost']['Amount']
                service['Currency'] = subentry['Metrics']['UnblendedCost']['Unit']
                day['Services'].append(service)
            result.append(day)

    return result