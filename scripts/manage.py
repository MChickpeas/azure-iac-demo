import json
import subprocess
import sys
import os

with open('config.json') as f:
    config = json.load(f)

def load_game(game_path):
    with open(os.path.join(game_path, 'game.json')) as f:
        return json.load(f)

def start(resource_group, vm_name):
    print(f"Starting {vm_name}...")
    subprocess.run([
        'az', 'vm', 'start',
        '--resource-group', resource_group,
        '--name', vm_name
    ], shell=True)

    result = subprocess.run([
        'az', 'vm', 'list-ip-addresses',
        '--resource-group', resource_group,
        '--name', vm_name,
        '--query', '[0].virtualMachine.network.publicIpAddresses[0].ipAddress',
        '--output', 'tsv'
    ], capture_output=True, text=True, shell=True)

    print(f"  ✓ Server is up — connect at: {result.stdout.strip()}")

def stop(resource_group, vm_name):
    print(f"Stopping {vm_name}...")
    subprocess.run([
        'az', 'vm', 'deallocate',
        '--resource-group', resource_group,
        '--name', vm_name
    ], shell=True)
    print("  ✓ Server stopped — no charges while deallocated")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python manage.py games/vein start")
        print("       python manage.py games/project-zomboid stop")
        sys.exit(1)

    game_path = sys.argv[1]
    command   = sys.argv[2]
    game      = load_game(game_path)

    resource_group = game['resource_group']
    vm_name        = f"{game['prefix']}-vm"

    if command == 'start':
        start(resource_group, vm_name)
    elif command == 'stop':
        stop(resource_group, vm_name)
    else:
        print(f"Unknown command '{command}' — use start or stop")
