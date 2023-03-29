import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Set the threshold values for CPU, disk usage, and memory utilization
    cpu_threshold = 50.0
    disk_threshold = 80.0
    memory_threshold = 80.0
    
    # Initialize the AWS clients
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    ses = boto3.client('ses')
    
    # Get information about all EC2 instances in the account
    instances = ec2.describe_instances().get('Reservations', [])
    
    # Loop through each instance and collect utilization metrics
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = ""
            
            # Retrieve the instance name from its tags, if available
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
            
            # Get CPU utilization metric
            cpu_metric = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id},
                ],
                StartTime='2023-03-26T00:00:00Z',
                EndTime='2023-03-26T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )
            
            # Get disk usage metric
            disk_metric = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='DiskSpaceUtilization',
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id},
                ],
                StartTime='2023-03-26T00:00:00Z',
                EndTime='2023-03-26T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )
            
            # Get memory utilization metric
            memory_metric = cloudwatch.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='MemoryUsage',
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id},
                ],
                StartTime='2023-03-26T00:00:00Z',
                EndTime='2023-03-26T23:59:59Z',
                Period=3600,
                Statistics=['Average']
            )
            
            # Check if any of the metrics are below the threshold values
            cpu_utilization = cpu_metric['Datapoints'][0]['Average']
            disk_usage = disk_metric['Datapoints'][0]['Average']
            memory_utilization = memory_metric['Datapoints'][0]['Average']
            message = ""
            
            if cpu_utilization < cpu_threshold:
                message += f"CPU utilization for {instance_name} is {cpu_utilization:.2f}%, which is below the threshold of {cpu_threshold:.2f}%.\n"
            
            if disk_usage > disk_threshold:
                message += f"Disk usage for {instance_name} is {disk_usage:.2f}%, which is above the threshold of {disk_threshold:.2f}%.\n"
            
            if memory_utilization > memory_threshold:
                message += f"Memory utilization for {instance_name} is {memory_utilization:.2f}%, which is above the threshold of {memory_threshold:.2f}"

            if message:
            # Send an email alert using SES
             sender = 'okumakube@gmail.com'
             recipient = 'okumakube@gmail.com'
             subject = f"Alert: EC2 instance {instance_name} is experiencing low utilization"
             body  = f"Hello,\n\nThe following issues have been detected with EC2 instance {instance_name}:\n\n{message}\n\nPlease take appropriate action to address these issues.\n\nBest regards,\nYour AWS Lambda function"
            
            try:
                response = ses.send_email(
                    Source=sender,
                    Destination={
                        'ToAddresses': [recipient],
                    },
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {'Text': {'Data': body}},
                    }
                )
                
                print(f"Email alert sent for {instance_name} ({instance_id}): {message}")
            
            except ClientError as e:
                print(f"Error sending email for {instance_name} ({instance_id}): {e.response['Error']['Message']}")
    