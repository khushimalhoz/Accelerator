import os
import argparse
import boto3
import aws_budget_logger
from otawslibs import generate_aws_session
from botocore.exceptions import ClientError

LOG_PATH = "aws-resource-scheduler.log"
LOGGER = aws_budget_logger._get_logging(LOG_PATH)

def _enable_cost_anomaly(args, session):
    cost_anomaly_client = session.client('ce')

    try:
        LOGGER.info(f"Creating anomaly monitor with name: {args.get('anomaly_monitor_name')}, type: {args.get('anomaly_monitor_type')}, dimension: {args.get('anomaly_monitor_dimension')}")
        
        monitor_details = cost_anomaly_client.create_anomaly_monitor(AnomalyMonitor={
            "MonitorName": args.get('anomaly_monitor_name', 'DefaultMonitorName'),
            "MonitorType": args.get('anomaly_monitor_type', 'DIMENSIONAL'),
            "MonitorDimension": args.get('anomaly_monitor_dimension', 'SERVICE')
        })
        LOGGER.info(f"Cost anomaly monitor '{args['anomaly_monitor_name']}' created successfully.")
        monitor_arn = monitor_details['MonitorArn']

        threshold = args.get('threshold', 100.0)

        LOGGER.info(f"Creating anomaly subscription with threshold: {threshold}")
        
        cost_anomaly_client.create_anomaly_subscription(
            AnomalySubscription={
                'MonitorArnList': [
                    monitor_arn,
                ],
                'Subscribers': [
                    {
                        'Address': email_address,
                        'Type': 'EMAIL',
                        'Status': 'CONFIRMED'
                    } for email_address in args['email_addresses']
                ],
                'Threshold': threshold,
                'Frequency': args['frequency'],
                'SubscriptionName': args['subscription_name']
            }
        )

        LOGGER.info(f"Cost anomaly subscription '{args['subscription_name']}' is attached to '{args['anomaly_monitor_name']}' monitor successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'DuplicateRecordException':
            LOGGER.warning(f"Cost anomaly monitor '{args['anomaly_monitor_name']}' already exists. {e}")
        else:
            LOGGER.error(f"Error creating cost anomaly monitor: {e}")
    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")

def _account_cost_anomaly_factory(args, aws_profile=None, role_arn=None):
    try:
        LOGGER.info("Connecting to AWS...")
        
        # Ensure to pass both aws_profile and role_arn to _create_session
        session = generate_aws_session._create_session(
            aws_profile=aws_profile,
            role_arn=role_arn
        )
        
        LOGGER.info("AWS connection established.")    
        _enable_cost_anomaly(args, session)
    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure! Please specify a valid AWS profile or use a valid IAM role.').with_traceback(e.__traceback__)
        else:
            raise e
    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")
