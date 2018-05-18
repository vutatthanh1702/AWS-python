codedeploy_applicationName= 'DeployApplication6660'
codedeploy_deploymentGroupName= 'deploytest'

ami_InstanceMasterId= 'i-32bfab96'

cfn_URLtemplate= 'https://s3-ap-southeast-1.amazonaws.com/6660/testcfn.template'

import boto3
import time

def createAMI(name):
    ec2client=   boto3.client('ec2', region_name='ap-southeast-1')
    amiCreate=   ec2client.create_image(
        InstanceId= ami_InstanceMasterId,
        Name= name[2]+ time.strftime("%Y%m%d-%H%M"),
        Description= 'AMI to test CloudFomation'
    )
    cloudFomation(amiCreate['ImageId'],name)

def cloudFomation(amiId,name):
    cfclient=   boto3.client('cloudformation', region_name='ap-southeast-1')
    cfStackCreate= cfclient.create_stack(
        StackName= name[1]+ '-'+ name[0],
        TemplateURL=cfn_URLtemplate,
        Parameters= [
            {'ParameterKey': 'LcImageId', 'ParameterValue': amiId, 'UsePreviousValue': False},
            {'ParameterKey': 'SuffixName', 'ParameterValue': name[0], 'UsePreviousValue': False},
            {'ParameterKey': 'WebServerName', 'ParameterValue': name[1], 'UsePreviousValue': False},
            {'ParameterKey': 'LcAssociatePublicIpAddress', 'ParameterValue': 'True', 'UsePreviousValue': False},
            {'ParameterKey': 'LbSubnet', 'ParameterValue': 'Public', 'UsePreviousValue': False}
        ],
        DisableRollback= False,

    )

def namesuffix(event, context):
    time.sleep(5)
    codedeploy= boto3.client('codedeploy', region_name='ap-southeast-1')
    listdeployment= codedeploy.list_deployments(
        applicationName=codedeploy_applicationName,
        deploymentGroupName=codedeploy_deploymentGroupName,
        includeOnlyStatuses=['Succeeded', 'Failed', 'Stopped', 'Created', 'Queued', 'InProgress']
    )
    getdeployment= codedeploy.get_deployment(
        deploymentId= listdeployment['deployments'][0]
    )
    namesuffix= getdeployment['deploymentInfo']['description'][len(getdeployment['deploymentInfo']['description'])-1]
    nameserver= getdeployment['deploymentInfo']['description'][:len(getdeployment['deploymentInfo']['description'])-2]
    aminame= nameserver[:len(nameserver)-3]
    name= (namesuffix, nameserver, aminame)
    createAMI(name)
