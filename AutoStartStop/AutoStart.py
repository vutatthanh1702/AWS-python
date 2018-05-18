#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import boto3

ec2 = boto3.resource('ec2')


def get_specified_tagged_instance_ids(target_tag):
    """
    get target tagged instance-id
    """
    try:
        instances = ec2.instances.filter(
            Filters=[
                {'Name': 'tag:%s' % target_tag, 'Values': ['11']},
                {'Name': 'instance-state-name', 'Values': ['stopped']}])
    except Exception, e:
        print(e)
        sys.exit(2)

    if not instances is None:
        i = []
        for instance in instances:
            i.append(instance.instance_id)
    else:
        print("not found target tagged instances")
        sys.exit(0)

    return i


def start_instances(target_tag):
    """
    start instances
    """
    try:
        instances = get_specified_tagged_instance_ids(target_tag)
    except Exception, e:
        print(e)
        sys.exit(2)

    for instance in instances:
        res = ec2.instances.filter(InstanceIds=[instance]).start()
        status_code = res[0]["ResponseMetadata"]["HTTPStatusCode"]
        if status_code == 200:
            print("operation complete. target -> %s" % instance)
        else:
            print("operation failed. target -> %s" % instance)
            sys.exit(1)


def lambda_handler(event, context):
    target_tag = "AutoStart"
    start_instances(target_tag)
    sys.exit(0)
