## Virtaul Environment Disable steps

Removing Virtual Environment and Installing Dependencies
This guide outlines the steps to remove a Python virtual environment and install required dependencies using pip.

1. Update Package List
First, update the system's package list to ensure that you have the latest versions of packages available.

```bash

sudo apt update
```

Explanation: This command updates the list of available packages from the repositories configured in your system, ensuring you have the latest version information.

2. Install Python3 Pip
Install python3-pip, the package installer for Python 3. It allows you to install Python libraries and dependencies.

```bash
sudo apt install python3-pip
```
Explanation: This command installs pip for Python 3, which is necessary for managing Python packages.

3. Install Specific Python Package
To install a Python package (e.g., json-log-formatter) globally, use pip with the --break-system-packages flag to bypass the system package restrictions.

```bash
python3 -m pip install json-log-formatter --break-system-packages
```
Explanation: The json-log-formatter package is installed here with the --break-system-packages option, which allows you to install packages that would otherwise conflict with system-installed Python packages.

4. Install Dependencies from requirements.txt
Next, install the dependencies listed in your requirements.txt file.

```bash
pip install -r requirements.txt --break-system-packages
```
Explanation: This command installs all the Python libraries specified in the requirements.txt file with the same flag to avoid conflicts with system packages.

5. Set Configuration Path
If the script requires a specific configuration file, export the path to this file using the export command.

```bash
export CONF_PATH=/home/ubuntu/budget-assume-role/aws-budget-accelerator/config/aws_budget_config_sample.yml
```
Explanation: This sets the CONF_PATH environment variable to the path of the configuration file required by your Python script. This ensures the script can read the correct configuration.

6. Re-run Python Script
Now that the configuration path is set, you can rerun your script to ensure it uses the correct configuration.

```bash
python3 aws_budget_factory.py
```
Explanation: This step re-runs the Python script with the configuration path now correctly set.




