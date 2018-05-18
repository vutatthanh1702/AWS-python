import boto3

TOPIC_ARN = 'arn:aws:sns:ap-northeast-1:140755326548:seta-aws_RunningInstanceReport'

def lambda_handler(event, context):
    try:
        # Check for EC2
        ec2 = boto3.client('ec2')
        ec2_resp = ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running']}] )

        ec2_count = len(ec2_resp['Reservations'])
        console.log(ec2_count);
        if not ec2_count == 0:
            send_message.append("[EC2 is running!!]")
            for i in range(0, ec2_count):
                send_message.append(ec2_resp['Reservations'][i]['Instances'][0]['Tags'][0]['Value'])
            send_message.append("")

        # Check for ELB

        elb = boto3.client('elb')
        elb_resp = elb.describe_load_balancers()

        elb_count = len(elb_resp['LoadBalancerDescriptions'])

        if not elb_count == 0:
            send_message.append("[ELB is running!!]")
            for i in range(0, elb_count):
                send_message.append(elb_resp['LoadBalancerDescriptions'][i]['LoadBalancerName'])
            send_message.append("")

        # Check for RDS

        rds = boto3.client('rds')
        rds_resp = rds.describe_db_instances()

        rds_count = len(rds_resp['DBInstances'])

        if not rds_count == 0:
            send_message.append("[RDS is running!!]")
            for i in range(0, rds_count):
                send_message.append(rds_resp['DBInstances'][i]['DBInstanceIdentifier'])
            send_message.append("")

        # Send mail

        send_subject = "[AWS]Money Save"
        send_message = ["Please check resources...\n"]

        for i in send_message:
            print(i)

        sns = boto3.client('sns')

        sns_resp = sns.publish(
            TopicArn = TOPIC_ARN,
            Message = "\n".join(send_message),
            Subject = send_subject
        )
        return 0
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
