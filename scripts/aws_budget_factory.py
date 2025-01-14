import sys, os, argparse
import boto3
import aws_budget_alerting
import aws_budget_logger
import aws_cost_anomaly_alerting
from otawslibs import generate_aws_session
from otfilesystemlibs import yaml_manager
from botocore.exceptions import ClientError

CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "aws-resource-scheduler.log"

LOGGER = aws_budget_logger._get_logging(LOG_PATH)

def _aws_budget_manager(args):
    try:
        LOGGER.info(f'Fetching properties from conf file: {args.property_file_path}.')

        yaml_loader = yaml_manager.getYamlLoader()
        properties = yaml_loader._loadYaml(args.property_file_path)

        LOGGER.info(f'Properties fetched from conf file.')

        if properties:
            for resources in properties['actions_on']:
                if "budget_alerting" in resources:
                    if "budget_alerting" in properties:
                        for budgets_details in properties["budget_alerting"]:
                            for budget in budgets_details.keys():
                                # Get the aws_profile and role_arn if provided
                                aws_profile = budgets_details[budget].get('aws_profile')
                                role_arn = budgets_details[budget].get('role_arn')

                                # Call _account_budget_factory with both aws_profile and role_arn if needed
                                aws_budget_alerting._account_budget_factory(budgets_details[budget], aws_profile, role_arn)
                elif "overall_aws_services" in resources:
                    if "budget_alerting" in resources["overall_aws_services"]:
                        if "budget_alerting" in properties["overall_aws_services"]:
                            for accounts_details in properties["overall_aws_services"]["budget_alerting"]:
                                for account_name in accounts_details.keys():
                                    aws_profile = accounts_details[account_name].get('aws_profile')
                                    role_arn = accounts_details[account_name].get('role_arn')
                                    aws_budget_alerting._account_budget_factory(accounts_details[account_name], aws_profile, role_arn)
                elif "overall_aws_tags" in resources:
                    if "budget_alerting" in resources["overall_aws_tags"]:
                        if "budget_alerting" in properties["overall_aws_tags"]:
                            for accounts_details in properties["overall_aws_tags"]["budget_alerting"]:
                                for account_name in accounts_details.keys():
                                    aws_profile = accounts_details[account_name].get('aws_profile')
                                    role_arn = accounts_details[account_name].get('role_arn')
                                    aws_budget_alerting._account_budget_factory(accounts_details[account_name], aws_profile, role_arn)
                elif "cost_anomaly" in resources:
                    if "cost_anomaly" in properties:
                        for accounts_details in properties["cost_anomaly"]:
                            for account_name in accounts_details.keys():
                                aws_profile = accounts_details[account_name].get('aws_profile')
                                role_arn = accounts_details[account_name].get('role_arn')
                                aws_cost_anomaly_alerting._account_cost_anomaly_factory(accounts_details[account_name], aws_profile, role_arn)
                else:
                    LOGGER.warning(f'Action {resources} params is not available in config, please check.')
    except Exception as e:
        LOGGER.error(f"Error processing budget manager: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default=os.environ.get(CONF_PATH_ENV_KEY), type=str)
    args = parser.parse_args()
    _aws_budget_manager(args)
