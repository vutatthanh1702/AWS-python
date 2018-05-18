# -*- coding: utf-8 -*-

from __future__ import print_function

import boto3
import json
import logging
import datetime

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError
REGION                  =['us-east-1','us-east-2','us-west-1','us-west-2',
                    'ca-central-1','eu-west-1','eu-central-1','eu-west-2','ap-northeast-1',
                    'ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-south-1','sa-east-1']
ACCOUNT_ID              ='977593584391'
todaydetail             =datetime.datetime.today()
today_check             =todaydetail.year*10000+todaydetail.month*100+todaydetail.day
HOOK_URL                ="https://hooks.slack.com/services/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"
SLACK_CHANNEL           ='#lambda_test1'
logger                  =logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        for region in REGION:
            instances = get_instances(region,['expri'])
            descriptions = {}
            for i in instances:
                tags = { t['Key']: t['Value'] for t in i['Tags'] }
                generation = int( tags.get('expri', 0) )
                if today_check>= generation:
                    send_Mess(region,tags.get('Name'))
            rdss=get_RDS(region)
            for x in rdss : 
                send_Mess(region,x)
        return 0
    except Exception as e:
        print(e)
        print('Error')
        raise e
def get_instances(region,tag_names):
    ec2=boto3.client(
            'ec2',
            region_name=region
    )
    reservations = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': tag_names
            }
        ]
    )['Reservations']

    return sum([
        [i for i in r['Instances']]
        for r in reservations
    ], [])
def get_RDS(region):
    RDS=boto3.client('rds', 
            region_name=region
    )
    resp = RDS.describe_db_instances()
    rds_list = []
    for rds in resp['DBInstances']:
        resp2 = RDS.list_tags_for_resource(
            ResourceName="arn:aws:rds:"+region+":"+ACCOUNT_ID+":db:" + rds['DBInstanceIdentifier']
        )
        for tag in resp2['TagList']:
            if tag['Key'] == 'expri' and today_check>=int(tag['Value']):
                rds_list.append(rds['DBInstanceIdentifier'])
    return rds_list
def send_Mess(region,resources_name):
    slack_message = {
                    'channel': SLACK_CHANNEL,
                    'text': region +'の'+ resources_name+'は期限切れです。'
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
                