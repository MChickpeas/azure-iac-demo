import json
import subprocess
import sys
import os

# Load base config
with open('config.json') as f:
    config = json.load(f)

SUBSCRIPTION_ID = config['subscription_id']
LOCATION        = config['location']

def load_game(game_path):
    game_json = os.path.join(game_path, 'game.json')
    with open(game_json) as f:
        return json.load(f)

def create_resource_group(resource_group):
    print(f"Creating resource group '{resource_group}'...")
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', LOCATION
    ], shell=True)
    print(f"  ✓ Resource group ready in {LOCATION}")

def deploy(game, resource_group):
    admin_password = input("Enter VM admin password: ")
    main_json = os.path.join(game['_path'], 'main.json')

    print(f"Starting {game['display_name']} deployment (this takes 3-5 minutes)...")
    result = subprocess.run([
        'az', 'deployment', 'group', 'create',
        '--resource-group', resource_group,
        '--template-file', main_json,
        '--parameters', f'adminPassword={admin_password}',
        '--parameters', f'prefix={game["prefix"]}',
        '--name', f'{game["name"]}-deployment'
    ], capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        print(f"  ✗ Deployment failed:\n{result.stderr}")
        return None

    output = json.loads(result.stdout)
    print(f"  ✓ Deployment complete — state: {output['properties']['provisioningState']}")
    return output

def log_resources(resource_group):
    print("\nResources created:")
    result = subprocess.run([
        'az', 'resource', 'list',
        '--resource-group', resource_group,
        '--query', '[].{type:type, name:name}',
        '--output', 'json'
    ], capture_output=True, text=True, shell=True)
    resources = json.loads(result.stdout)
    for r in resources:
        rtype = r['type'].split('/')[-1]
        print(f"  • {rtype:<25} {r['name']}")

def build_bicep(game_path):
    print("Building Bicep template...")
    subprocess.run([
        'az', 'bicep', 'build',
        '--file', os.path.join(game_path, 'main.bicep'),
        '--outfile', os.path.join(game_path, 'main.json')
    ], shell=True)
    print("  ✓ Template built")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python deploy_server.py games/vein")
        print("       python deploy_server.py games/project-zomboid")
        sys.exit(1)

    game_path = sys.argv[1]
    game = load_game(game_path)
    game['_path'] = game_path
    resource_group = game['resource_group']

    print(f"\nDeploying {game['display_name']} server...")
    print(f"  App ID:   {game['app_id']}")
    print(f"  Ports:    {game['ports']}")
    print(f"  VM size:  {game['vm_size']}")
    print(f"  RG:       {resource_group}\n")

    build_bicep(game_path)
    create_resource_group(resource_group)
    deploy(game, resource_group)
    log_resources(resource_group)
