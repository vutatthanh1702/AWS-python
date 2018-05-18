import boto3

access_key = '****'
secret_key = '****'
region = 'ap-northeast-1'
backup_generation = 3

def create_snapshot(event, context):
    session = boto3.session.Session(region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    ec2 = session.resource('ec2')
    notification_title = 'スナップショット作成完了'
    notification_list = []
    snapshotid_list = []
    volume_ids = ['vol-********']
    for i in range(len(volume_ids)):
        try:
            description = 'Created by AWS Lambda from %s' % volume_ids[i]
            snapshot = ec2.create_snapshot(VolumeId=volume_ids[i], Description=description)
            snapshotid_list.append(snapshot.id)
            temporary_text = 'EBSボリューム %s のスナップショット %s を作成しました。' % (volume_ids[i], snapshot.id)
            notification_list.append(temporary_text)
        except:
            temporary_text = 'EBSボリューム %s のスナップショット作成に失敗しました。' % volume_ids[i]
            notification_list.append(temporary_text)
            notification_title = 'スナップショット作成失敗'
            continue

    # 不要なスナップショットの削除
    for volume_id in volume_ids:
        snapshot = {}  # EBSスナップショットIDと取得日時が入るディクショナリ
        for snapshot_object in ec2.snapshots.filter(OwnerIds=['self'], Filters=[{'Name':'volume-id', 'Values':[volume_id]}]):
            temp_dict = {snapshot_object.id:snapshot_object.start_time}
            snapshot.update(temp_dict)
        snapshot = sorted(snapshot.items(), key=lambda (k, v): (v, k), reverse=True)
        snapshot_count = len(snapshot)
        if backup_generation < snapshot_count:
            temporary_text = '%s の不要なEBSスナップショットの削除を開始します。' % volume_id
            notification_list.append(temporary_text)
            for i in range(backup_generation, snapshot_count):
                try:
                    ec2.Snapshot(snapshot[i][0]).delete()
                    temporary_text = 'EBSスナップショット %s を削除しました。' % snapshot[i][0]
                    notification_list.append(temporary_text)
                except:
                    temporary_text = 'EBSスナップショット %s の削除に失敗しました。' % snapshot[i][0]
                    notification_list.append(temporary_text)
                    continue
        else:
            temporary_text = '%s のEBSスナップショットの数が指定世代数以下なので、EBSスナップショットは削除されませんでした。' % volume_id
            notification_list.append(temporary_text)
    notification_text = '\n'.join(notification_list)

    # SNSでメール送信
    sns = session.client('sns')
    topic = 'arn:aws:sns:ap-northeast-1:************:create_snapshot'
    sns.publish(TopicArn=topic, Message=notification_text, Subject=notification_title)
