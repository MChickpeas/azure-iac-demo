import json
import subprocess

with open('config.json') as f:
    config = json.load(f)

SUBSCRIPTION_ID = config['subscription_id']
RESOURCE_GROUP  = 'vein-server-rg'
LOCATION        = config['location']

def create_resource_group():
    print(f"Creating resource group '{RESOURCE_GROUP}'...")
    subprocess.run([
        'az', 'group', 'create',
        '--name', RESOURCE_GROUP,
        '--location', LOCATION
    ], shell=True)
    print(f"  ✓ Resource group ready in {LOCATION}")

def deploy():
    admin_password = input("Enter VM admin password: ")

    print("Starting deployment (this takes 3-5 minutes)...")
    result = subprocess.run([
        'az', 'deployment', 'group', 'create',
        '--resource-group', RESOURCE_GROUP,
        '--template-file', 'game-server/main.json',
        '--parameters', f'adminPassword={admin_password}',
        '--parameters', 'prefix=vein-server',
        '--name', 'vein-server-deployment'
    ], capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        print(f"  ✗ Deployment failed:\n{result.stderr}")
        return None

    output = json.loads(result.stdout)
    print(f"  ✓ Deployment complete — state: {output['properties']['provisioningState']}")
    return output

def log_resources():
    print("\nResources created:")
    result = subprocess.run([
        'az', 'resource', 'list',
        '--resource-group', RESOURCE_GROUP,
        '--query', '[].{type:type, name:name}',
        '--output', 'json'
    ], capture_output=True, text=True, shell=True)
    resources = json.loads(result.stdout)
    for r in resources:
        rtype = r['type'].split('/')[-1]
        print(f"  • {rtype:<25} {r['name']}")

if __name__ == '__main__':
    create_resource_group()
    deploy()
    log_resources()
