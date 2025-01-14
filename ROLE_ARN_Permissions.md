# AWS Role Permissions for Server

This document outlines the permissions attached to the AWS IAM role that will be assigned to the server. The role includes access to various AWS services necessary for managing billing and cost-related tasks.

## IAM Role Permissions

The role has the following permissions attached:

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "budgets:*",
                "ce:*",
                "billing:*"
            ],
            "Resource": "*"
        }
    ]
}

```

### Permissions Breakdown
- **budgets:***: Grants full access to AWS Budgets, enabling the creation, modification, and deletion of budgets and budget-related actions.
- **ce:***: Grants full access to AWS Cost Explorer (CE), allowing the user to retrieve and analyze cost and usage data.
- **billing:***: Grants full access to billing information, enabling actions related to the billing account, including viewing and managing charges, payments, and invoices.
These permissions allow the role to manage AWS billing, budgets, and cost-related resources effectively.

![image](https://github.com/user-attachments/assets/cd282c9f-a68a-4ccb-842a-d989d66150e5)
![image](https://github.com/user-attachments/assets/06855d12-2edb-4f2f-85b1-dee320074bc6)


> **Note:**This markdown document provides a clear overview of the permissions associated with the IAM role.

