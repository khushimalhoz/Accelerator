import os
import argparse
import boto3
import aws_budget_logger
from otawslibs import generate_aws_session
from botocore.exceptions import ClientError
import time

LOG_PATH = "aws-resource-scheduler.log"

LOGGER = aws_budget_logger._get_logging(LOG_PATH)

SERVICE_NAME_MAPPING = {
    "EC2": "Amazon Elastic Compute Cloud - Compute",
    "ECR": "Amazon EC2 Container Registry (ECR)",
    "SQS": "Amazon Simple Queue Service",
    "Tax": "Tax",
    "Athena": "Amazon Athena",
    "SES": "Amazon Simple Email Service",
    "SNS": "Amazon Simple Notification Service",
    "VPC": "Amazon Virtual Private Cloud",
    "WAF": "AWS WAF",
    "ECS": "Amazon EC2 Container Service",
    "EKS": "Amazon Elastic Container Service for Kubernetes",
    "EBS": "Amazon Elastic Block Store",
    "CloudFront": "Amazon CloudFront",
    "CloudTrail": "AWS CloudTrail",
    "CloudWatch": "AmazonCloudWatch",
    "Cognito": "Amazon Cognito",
    "Config": "AWS Config",
    "DynamoDB": "Amazon DynamoDB",
    "DMS": "AWS Database Migration Service",
    "ElastiCache": "Amazon ElastiCache",
    "Elasticsearch": "Amazon Elasticsearch Service",
    "ELB": "Amazon Elastic Load Balancing",
    "APIGateway": "Amazon API Gateway",
    "Glue": "AWS Glue",
    "Kafka": "Managed Streaming for Apache Kafka",
    "KMS": "AWS Key Management Service",
    "Kinesis": "Amazon Kinesis",
    "Lambda": "AWS Lambda",
    "Lex": "Amazon Lex",
    "Matillion": "Matillion ETL for Amazon Redshift",
    "Pinpoint": "AWS Pinpoint",
    "Polly": "Amazon Polly",
    "Rekognition": "Amazon Rekognition",
    "RDS": "Amazon Relational Database Service",
    "Redshift": "Amazon Redshift",
    "S3": "Amazon Simple Storage Service",
    "SFTP": "AWS Transfer for SFTP",
    "Route53": "Amazon Route 53",
    "SageMaker": "Amazon SageMaker",
    "SecretsManager": "AWS Secrets Manager",
    "XRay": "AWS X-Ray"
}

RI_SERVICES = {
    "EC2": "Amazon Elastic Compute Cloud - Compute",
    "RDS": "Amazon Relational Database Service",
    "Redshift": "Amazon Redshift",
    "ElastiCache": "Amazon ElastiCache",
    "Elasticsearch": "Amazon Elasticsearch Service"
}

def _validate_services(services, service_mapping):
    for service in services:
        if service not in service_mapping:
            return False, service
    return True, None

def _enable_budget_alerting(args, session):
    budgets_client = session.client('budgets')

   
    service_mapping = RI_SERVICES if args['budget_type'] == 'RI_UTILIZATION' else SERVICE_NAME_MAPPING

    # Validate cost_filters services if present
    if 'cost_filters' in args and 'services' in args['cost_filters']:
        services_valid, invalid_service = _validate_services(args['cost_filters']['services'], service_mapping)
        if not services_valid:
            LOGGER.warning(f"Service '{invalid_service}' is not supported,Kindly add the proper service name from README.")
            return

    # Define the budget parameters
    budget_parameters = {
        'BudgetName': args['budget_name'],
        'BudgetType': args['budget_type'],
        'TimeUnit': args['budget_time_unit'],
    }

    if args["budget_type"] != "RI_UTILIZATION":
        budget_parameters['BudgetLimit'] = {
            'Amount': str(args['budget_limit_amount']),
            'Unit': args['budget_limit_unit'],
        }
        budget_parameters['CostTypes'] = args['cost_types_parameters']

    if 'cost_filters' in args:
        cost_filter = {}
        if 'services' in args['cost_filters']:
            if args['budget_type'] == 'RI_UTILIZATION':
                cost_filter['Service'] = [RI_SERVICES[service] for service in args['cost_filters']['services']]
            else:
                cost_filter['Service'] = [SERVICE_NAME_MAPPING[service] for service in args['cost_filters']['services']]
        if 'tags' in args['cost_filters']:
            tag_key_values = [f"{tag['Key']}${tag['Values'][0]}" for tag in args['cost_filters']['tags']]
            cost_filter["TagKeyValue"] = tag_key_values
        budget_parameters['CostFilters'] = cost_filter

    try:
        # Check if budget exists and delete if recreate flag is true
        is_budget_exists = budgets_client.describe_budget(
            AccountId=args['account_id'],
            BudgetName=args['budget_name']
        )
        if is_budget_exists and args['recreate_budget_if_needed']:
            response = budgets_client.delete_budget(
                AccountId=args['account_id'],
                BudgetName=args['budget_name']
            )
            LOGGER.info(f"Succesfully removed existing budget {args['budget_name']}. Now creating a new one.")
        else:
            LOGGER.error(f"Budget {args['budget_name']} already exists and recreate_budget_if_needed is set to False.")
            exit(0)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NotFoundException':
            LOGGER.info("Budget doesn't exist. Creating a new one.")
        else:
            LOGGER.error(f"Error checking for existing budget: {e}")
            return

    try:
        # Create the budget
        response = budgets_client.create_budget(
            AccountId=args['account_id'],
            Budget=budget_parameters
        )

        LOGGER.info("Response from create_budget API call: {}".format(response))

        # Create actual notification with multiple subscribers (email addresses)
        create_actual_notification_response = budgets_client.create_notification(
            AccountId=args['account_id'],
            BudgetName=args['budget_name'],
            Notification={
                'NotificationType': args['actual_threshold_notification'],
                'ComparisonOperator': args['actual_budget_comparison_operator'],
                'Threshold': args['actual_budget_threshold'],
                'ThresholdType': args['threshold_type'],
                'NotificationState': 'ALARM',
            },
            Subscribers=[
                {
                    'SubscriptionType': 'EMAIL',
                    'Address': email_address,
                } for email_address in args['email_addresses']
            ]
        )

        # Create forecasted notification with multiple subscribers (email addresses)
        if args["budget_type"] != "RI_UTILIZATION":
            create_forecasted_notification_response = budgets_client.create_notification(
                AccountId=args['account_id'],
                BudgetName=args['budget_name'],
                Notification={
                    'NotificationType': args['forecasted_threshold_notification'],
                    'ComparisonOperator': args['forecasted_budget_comparison_operator'],
                    'Threshold': args['forecasted_budget_threshold'],
                    'ThresholdType': args['threshold_type'],
                    'NotificationState': 'ALARM',
                },
                Subscribers=[
                    {
                        'SubscriptionType': 'EMAIL',
                        'Address': email_address,
                    } for email_address in args['email_addresses']
                ]
            )

        LOGGER.info(f"AWS Budget '{args['budget_name']}' created successfully.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'DuplicateRecordException':
            LOGGER.warning(f"AWS Budget '{args['budget_name']}' already exists. {e}")
        else:
            LOGGER.error(f"Error creating AWS Budget: {e}")

def _account_budget_factory(args, aws_profile=None, role_arn=None):
    try:
        LOGGER.info("Connecting to AWS...")
        
        # Ensure to pass both aws_profile and role_arn to _create_session
        session = generate_aws_session._create_session(
            aws_profile=aws_profile,
            role_arn=role_arn
        )
        
        LOGGER.info("AWS connection established.")
        _enable_budget_alerting(args, session)
    except ClientError as e:
        LOGGER.error(f"Client error during budget creation: {e}")
        raise
    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")
        raise
