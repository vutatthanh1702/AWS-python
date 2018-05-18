# -*- coding: utf-8 -*-

import commands, boto3

TARGET_INSTANCE_NAME = "i-8cef6013" # Enter your target Instance Name
GEM_NUM = 2 # 保存世代数

def _(cmd):
    return commands.getoutput(cmd)

def handler(event, context):
    images = boto3.client('ec2').describe_images(Owners=["self"])["Images"]

    delete_count = len(images) - GEM_NUM
    targetImages = []
    for image in sorted(images, key=lambda x: x["CreationDate"]):
        if (delete_count == 0) :
            break
        elif image["Name"].count(TARGET_INSTANCE_NAME):
            targetImages.append(image)
            delete_count -= 1

    for targetImage in targetImages:
        ec2 = boto3.resource('ec2')
        ec2.Image(targetImage["ImageId"]).deregister()
        for block in targetImage["BlockDeviceMappings"]:
            ec2.Snapshot(block["Ebs"]["SnapshotId"]).delete()
