import json
import subprocess
import sys

with open('config.json') as f:
    config = json.load(f)

RESOURCE_GROUP = 'vein-server-rg'
VM_NAME        = 'vein-server-vm'
SUBSCRIPTION   = config['subscription_id']

def start():
    print(f"Starting {VM_NAME}...")
    subprocess.run([
        'az', 'vm', 'start',
        '--resource-group', RESOURCE_GROUP,
        '--name', VM_NAME
    ], shell=True)
    
    # Get and print the public IP after starting
    result = subprocess.run([
        'az', 'vm', 'list-ip-addresses',
        '--resource-group', RESOURCE_GROUP,
        '--name', VM_NAME,
        '--query', '[0].virtualMachine.network.publicIpAddresses[0].ipAddress',
        '--output', 'tsv'
    ], capture_output=True, text=True, shell=True)
    
    print(f"  ✓ Server is up — connect at: {result.stdout.strip()}")

def stop():
    print(f"Stopping {VM_NAME}...")
    subprocess.run([
        'az', 'vm', 'deallocate',
        '--resource-group', RESOURCE_GROUP,
        '--name', VM_NAME
    ], shell=True)
    print("  ✓ Server stopped — no charges while deallocated")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage.py start | stop")
    elif sys.argv[1] == 'start':
        start()
    elif sys.argv[1] == 'stop':
        stop()
    else:
        print(f"Unknown command '{sys.argv[1]}' — use start or stop")
