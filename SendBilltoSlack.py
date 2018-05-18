# -*- coding: utf-8 -*-

from __future__ import print_function

import boto3
import json
import logging
import datetime

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError



HOOK_URL                ="https://hooks.slack.com/services/xxx"
SLACK_CHANNEL           ='#ge_server'
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('cloudwatch')


def lambda_handler(event, context):
    logger.info("Event: " + str(event))

    startDate = datetime.datetime.today() - datetime.timedelta(days = 1)
    response = client.get_metric_statistics (
        MetricName = 'EstimatedCharges',
        Namespace  = 'AWS/Billing',
        Period     = 86400,
        StartTime  = startDate,
        EndTime    = datetime.datetime.today(),
        Statistics = ['Maximum'],
        Dimensions = [
            {'Name': 'LinkedAccount', 'Value': '14075xxx' },
            {
                'Name': 'Currency',
                'Value': 'USD'
            }
        ]
    )
    response004 = client.get_metric_statistics (
        MetricName = 'EstimatedCharges',
        Namespace  = 'AWS/Billing',
        Period     = 86400,
        StartTime  = startDate,
        EndTime    = datetime.datetime.today(),
        Statistics = ['Maximum'],
        Dimensions = [
            {'Name': 'LinkedAccount', 'Value': '3593xxx' },
            {
                'Name': 'Currency',
                'Value': 'USD'
            }
        ]
    )


    maximum = response['Datapoints'][0]['Maximum']
    maximum004 = response004['Datapoints'][0]['Maximum']
    print("Total score for", response)
    date    = response['Datapoints'][0]['Timestamp'].strftime('%Y年%m月%d日')

    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': "~%s\nAWS002の料金は$%sです。\n AWS004の料金は$%sです。" % (date, maximum,maximum004)
    }

    req = Request(HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
