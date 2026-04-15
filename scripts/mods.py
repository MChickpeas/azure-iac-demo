import json
import subprocess
import sys
import os

# TODO: implement mod management
# Usage:
#   python scripts/mods.py games/project-zomboid add 2392987397 BetterBuilding
#   python scripts/mods.py games/project-zomboid remove 2392987397 BetterBuilding
#   python scripts/mods.py games/project-zomboid list

def load_game(game_path):
    with open(os.path.join(game_path, 'game.json')) as f:
        return json.load(f)

def get_server_ip(resource_group, vm_name):
    # TODO: get the server IP so we can SSH in
    pass

def add_mod(ip, game, workshop_id, mod_id):
    # TODO: SSH into the VM and add the mod to the server config
    # 1. Read the current config file at game['mod_config_path']
    # 2. Append workshop_id to WorkshopItems= line
    # 3. Append mod_id to Mods= line
    # 4. Restart the server service
    pass

def remove_mod(ip, game, workshop_id, mod_id):
    # TODO: SSH into the VM and remove the mod from the server config
    # 1. Read the current config file at game['mod_config_path']
    # 2. Remove workshop_id from WorkshopItems= line
    # 3. Remove mod_id from Mods= line
    # 4. Restart the server service
    pass

def list_mods(ip, game):
    # TODO: SSH into the VM and print the current mods
    # 1. Read the config file at game['mod_config_path']
    # 2. Print WorkshopItems and Mods lines
    pass

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python mods.py games/project-zomboid add <workshop_id> <mod_id>")
        print("       python mods.py games/project-zomboid remove <workshop_id> <mod_id>")
        print("       python mods.py games/project-zomboid list")
        sys.exit(1)

    game_path = sys.argv[1]
    command   = sys.argv[2]
    game      = load_game(game_path)

    vm_name        = f"{game['prefix']}-vm"
    resource_group = game['resource_group']

    # TODO: replace with get_server_ip() once implemented
    ip = input("Enter server IP: ")

    if command == 'add' and len(sys.argv) == 5:
        add_mod(ip, game, sys.argv[3], sys.argv[4])
    elif command == 'remove' and len(sys.argv) == 5:
        remove_mod(ip, game, sys.argv[3], sys.argv[4])
    elif command == 'list':
        list_mods(ip, game)
    else:
        print(f"Unknown command '{command}'")
