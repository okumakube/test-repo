import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    cw = boto3.client('cloudwatch')

    reservations = ec2.describe_instances().get('Reservations', [])

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # CPU usage
            cpu = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime='2023-03-27T00:00:00Z',
                EndTime='2023-03-27T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )

            # Disk usage
            disk = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='DiskSpaceUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime='2023-03-27T00:00:00Z',
                EndTime='2023-03-27T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )

            # Memory usage
            mem = cw.get_metric_statistics(
                Namespace='System/Linux',
                MetricName='MemoryUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime='2023-03-27T00:00:00Z',
                EndTime='2023-03-27T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )

            # Send metrics to CloudWatch
            cw.put_metric_data(
                Namespace='Custom',
                MetricData=[
                    {
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ],
                        'Timestamp': cpu['Datapoints'][0]['Timestamp'],
                        'Value': cpu['Datapoints'][0]['Average']
                    },
                    {
                        'MetricName': 'DiskSpaceUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ],
                        'Timestamp': disk['Datapoints'][0]['Timestamp'],
                        'Value': disk['Datapoints'][0]['Average']
                    },
                    {
                        'MetricName': 'MemoryUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ],
                        'Timestamp': mem['Datapoints'][0]['Timestamp'],
                        'Value': mem['Datapoints'][0]['Average']
                    },
                ]
            )
