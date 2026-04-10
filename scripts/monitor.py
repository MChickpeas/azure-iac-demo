import socket
import json
import subprocess
import time
from datetime import datetime

with open('config.json') as f:
    config = json.load(f)

RESOURCE_GROUP = 'vein-server-rg'
VM_NAME        = 'vein-server-vm'
GAME_PORT      = 7777
CHECK_INTERVAL = 60   # check every 60 seconds

def get_server_ip():
    result = subprocess.run([
        'az', 'vm', 'list-ip-addresses',
        '--resource-group', RESOURCE_GROUP,
        '--name', VM_NAME,
        '--query', '[0].virtualMachine.network.publicIpAddresses[0].ipAddress',
        '--output', 'tsv'
    ], capture_output=True, text=True, shell=True)
    return result.stdout.strip()

def is_server_up(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(b'ping', (ip, GAME_PORT))
        sock.close()
        return True
    except Exception:
        return False

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {message}"
    print(line)
    with open('server_log.txt', 'a') as f:
        f.write(line + '\n')

if __name__ == '__main__':
    print("Starting monitor — press Ctrl+C to stop")
    ip = get_server_ip()
    log(f"Monitoring {VM_NAME} at {ip}:{GAME_PORT}")

    was_up = True
    while True:
        up = is_server_up(ip)
        if up and not was_up:
            log("✓ Server is back up")
        elif not up and was_up:
            log("✗ Server is DOWN — check Azure portal")
        was_up = up
        time.sleep(CHECK_INTERVAL)
