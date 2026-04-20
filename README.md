# Azure Game Server Platform

Deploys and manages dedicated game servers on Azure using modular Bicep templates and Python automation. Each game is fully defined in code — infrastructure, first-boot configuration, and server settings — so any server can be reproduced from scratch with a single command.

Also includes a standalone IaC portfolio demo that deploys a multi-resource Azure environment.

---

## Projects

### 1. IaC Demo (`infra/`)
A multi-resource Azure environment demonstrating core IaC concepts.

**Resources deployed:**
- Virtual Network + Subnet
- Storage Account
- Linux VM (Ubuntu 22.04)

### 2. VEIN Game Server (`games/vein/`)
Dedicated server for the VEIN zombie survival game.

- VM: Standard_DC4ds_v3 (Intel, 4 vCPU, 16 GB RAM) — Intel required for VEIN's physics engine
- Ports: 7777 (game), 27015 (Steam query)
- Auto-installs SteamCMD + VEIN on first boot via cloud-init
- Steam SDR networking via Game Server Login Token (GSLT)

### 3. Project Zomboid Server (`games/project-zomboid/`)
Dedicated server for Project Zomboid.

- VM: Standard_DC4ds_v3 (4 vCPU, 16 GB RAM)
- Ports: 16261 (game), 16262 (UDP)
- Auto-installs SteamCMD + PZ on first boot via cloud-init

---

## Project Structure

```
├── infra/
│   ├── main.bicep                  # Entry point for IaC demo
│   ├── network.bicep               # Virtual Network + Subnet
│   ├── storage.bicep               # Storage Account
│   └── vm.bicep                    # Network Interface + Linux VM
│
├── games/
│   ├── shared/
│   │   └── server.bicep            # Reusable module: NSG, Public IP, NIC, VM
│   ├── vein/
│   │   ├── main.bicep              # VEIN entry point (calls shared/server.bicep)
│   │   ├── game.json               # VEIN config: ports, VM size, budget
│   │   └── cloud-init.yml          # First-boot: SteamCMD, VEIN, systemd (git-ignored)
│   └── project-zomboid/
│       ├── main.bicep              # PZ entry point
│       ├── game.json               # PZ config: ports, VM size, budget
│       └── cloud-init.yml          # First-boot: SteamCMD, PZ, systemd (git-ignored)
│
├── scripts/
│   ├── deploy.py                   # Deploy the IaC demo environment
│   ├── deploy_server.py            # Deploy any game server (reads game.json)
│   ├── manage.py                   # Start / stop a game server VM
│   ├── monitor.py                  # UDP health check, logs to server_log.txt
│   └── mods.py                     # Mod management via SSH (skeleton)
│
└── config.json                     # Subscription settings + alert email (git-ignored)
```

---

## Prerequisites

- [Azure CLI](https://aka.ms/installazurecliwindows)
- Python 3.8+
- An Azure account — `az login`

---

## Setup

1. Clone the repo
2. Create `config.json` in the root:

```json
{
  "subscription_id": "your-subscription-id",
  "resource_group": "iac-demo-rg",
  "location": "eastus2",
  "prefix": "iac-demo",
  "alert_email": "your@email.com"
}
```

> `config.json` and `cloud-init.yml` files are git-ignored because they contain credentials (VM password prompts, GSLT tokens, server passwords).

---

## IaC Demo Deployment

```
python scripts/deploy.py
```

Prompts for a VM admin password, deploys all resources, and logs what was created.

**Cleanup:**
```
az group delete --name iac-demo-rg --yes
```

---

## Game Server Deployment

Pass the game folder as the argument:

```
python scripts/deploy_server.py games/vein
python scripts/deploy_server.py games/project-zomboid
```

This will:
1. Build the Bicep template
2. Create the resource group
3. Deploy all Azure resources (VNet, NSG, Public IP, NIC, VM)
4. Create a monthly budget alert (emails at 80% and 100% of `budget_usd`)

After deployment, cloud-init runs on the VM in the background. It takes **8–10 minutes** to install SteamCMD and download the game. Monitor progress:

```bash
ssh azureuser@<vm-ip>
sudo tail -f /var/log/cloud-init-output.log
```

When you see `Cloud-init finished`, check the server service:

```bash
sudo systemctl status vein-server
sudo systemctl status pz-server
```

### VEIN-specific: GSLT token required

VEIN uses Steam SDR networking. Before deploying, you need a Game Server Login Token:

1. Go to https://steamcommunity.com/dev/managegameservers
2. Enter App ID **1857950**, create the token
3. Add it to `games/vein/cloud-init.yml` under `[OnlineSubsystemSteam]`:

```ini
GameServerToken=YOUR_TOKEN_HERE
```

Without this token the server runs but cannot be found or joined through Steam.

---

## Start / Stop Servers

Always stop servers when not in use — `stop` deallocates the VM so you are not billed for compute.

```
python scripts/manage.py games/vein start
python scripts/manage.py games/vein stop

python scripts/manage.py games/project-zomboid start
python scripts/manage.py games/project-zomboid stop
```

---

## Monitor Server Health

```
python scripts/monitor.py games/vein
```

Sends a UDP ping every 60 seconds and logs uptime history to `server_log.txt`.

---

## Server Password

Each game's password is set in its `cloud-init.yml` (git-ignored). To change the VEIN password on a live server without redeploying:

```bash
sudo -u steamuser sed -i 's/ServerPassword=.*/ServerPassword=newpassword/' \
  /home/steamuser/vein/Vein/Saved/Config/LinuxServer/Game.ini
sudo systemctl restart vein-server
```

---

## Adding a New Game

1. Create a `games/<game-name>/` folder
2. Add `game.json` with `name`, `display_name`, `app_id`, `ports`, `vm_size`, `resource_group`, `prefix`, `budget_usd`
3. Add `main.bicep` calling `../shared/server.bicep` with the game's ports
4. Add `cloud-init.yml` to install and configure the game server
5. Deploy:

```
python scripts/deploy_server.py games/<game-name>
```

---

## Cleanup

```
az group delete --name vein-server-rg --yes
az group delete --name pz-server-rg --yes
az group delete --name iac-demo-rg --yes
```
