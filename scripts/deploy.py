import json
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import subprocess

# Load config
with open('config.json') as f:
    config = json.load(f)

SUBSCRIPTION_ID = config['subscription_id']
RESOURCE_GROUP  = config['resource_group']
LOCATION        = config['location']

# Authenticate using az login session
credential = DefaultAzureCredential()
client = ResourceManagementClient(credential, SUBSCRIPTION_ID)

def create_resource_group():
    print(f"Creating resource group '{RESOURCE_GROUP}'...")
    rg = client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {'location': LOCATION}
    )
    print(f"  ✓ Resource group ready in {rg.location}")
    return rg

def create_budget(email):
    print("Setting up $1 budget alert...")
    subprocess.run([
        'az', 'consumption', 'budget', 'create',
        '--budget-name', 'iac-demo-budget',
        '--amount', '1',
        '--time-grain', 'Monthly',
        '--start-date', '2026-04-01',
        '--end-date',   '2027-04-01',
        '--resource-group', RESOURCE_GROUP,
        '--category', 'Cost',
        '--threshold', '80',
        '--contact-emails', email
    ], shell=True)
    print("  ✓ Budget alert set — you'll get emailed at 80% ($0.80)")


def deploy():
    admin_password = input("Enter VM admin password: ")

    print("Starting deployment (this takes 3-5 minutes)...")
    result = subprocess.run([
        'az', 'deployment', 'group', 'create',
        '--resource-group', RESOURCE_GROUP,
        '--template-file', 'infra/main.json',
        '--parameters', f'adminPassword={admin_password}',
        '--parameters', f'prefix={config["prefix"]}',
        '--name', 'iac-demo-deployment'
    ], capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        print(f"  ✗ Deployment failed:\n{result.stderr}")
        return None

    output = json.loads(result.stdout)
    print(f"  ✓ Deployment complete — state: {output['properties']['provisioningState']}")
    return output

def log_resources():
    print("\nResources created:")
    resources = client.resources.list_by_resource_group(RESOURCE_GROUP)
    for r in resources:
        print(f"  • {r.type.split('/')[-1]:<25} {r.name}")


if __name__ == '__main__':
    create_resource_group()
    create_budget(input("Enter your email for budget alerts: "))
    deploy()
    log_resources()
