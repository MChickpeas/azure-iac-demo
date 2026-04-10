# Azure IaC Deployment Automation

Deploys multi-resource Azure environments using modular Bicep templates, automated with Python scripts. Includes a portfolio demo environment and a live VEIN game server deployment.

## Projects

### 1. IaC Demo (`infra/`)
A multi-resource Azure environment demonstrating core IaC concepts.

**Resources deployed:**
- Virtual Network + Subnet
- Storage Account
- Linux VM (Ubuntu 22.04) with Network Interface

### 2. VEIN Game Server (`game-server/`)
A production game server for the VEIN zombie survival game, deployed and managed entirely from code.

**Resources deployed:**
- Virtual Network + Subnet
- Network Security Group (ports 7777 + 27015 UDP open for VEIN)
- Static Public IP
- Network Interface
- Linux VM (Ubuntu 22.04, 4 core, 16GB RAM, 64GB SSD)

**Auto-installs on first boot via cloud-init:**
- SteamCMD
- VEIN Dedicated Server (App ID 2131400)
- Systemd service (auto-restarts if server crashes)

## Project Structure

```
├── infra/
│   ├── main.bicep              # Entry point for demo environment
│   ├── network.bicep           # Virtual Network + Subnet
│   ├── storage.bicep           # Storage Account
│   └── vm.bicep                # Network Interface + Linux VM
├── game-server/
│   ├── main.bicep              # Entry point for game server
│   ├── network.bicep           # Virtual Network + Subnet
│   ├── server.bicep            # Public IP, NSG, NIC, VM
│   └── cloud-init.yml          # First boot install script
├── scripts/
│   ├── deploy.py               # Deploy the IaC demo environment
│   ├── deploy_server.py        # Deploy the game server
│   ├── manage.py               # Start/stop the game server VM
│   └── monitor.py              # Monitor server uptime + log alerts
└── config.json                 # Your subscription settings (not committed)
```

## Prerequisites

- [Azure CLI](https://aka.ms/installazurecliwindows)
- Python 3.8+
- An Azure account (`az login`)

## Setup

1. Clone the repo
2. Create `config.json` in the root:

```json
{
  "subscription_id": "your-subscription-id",
  "resource_group": "iac-demo-rg",
  "location": "eastus2",
  "prefix": "iac-demo"
}
```

3. Install Python dependencies:

```
pip install azure-mgmt-resource azure-identity
```

---

## IaC Demo Deployment

```
az bicep build --file infra/main.bicep --outfile infra/main.json
python scripts/deploy.py
```

Prompts for your email (budget alerts) and a VM admin password, then deploys all resources and logs what was created.

**Cleanup:**
```
az group delete --name iac-demo-rg --yes
```

---

## Game Server Deployment

```
az bicep build --file game-server/main.bicep --outfile game-server/main.json
python scripts/deploy_server.py
```

Wait ~10 minutes after deployment for cloud-init to finish installing the VEIN server.

**Start/stop the server:**
```
python scripts/manage.py start
python scripts/manage.py stop
```

Always stop the server when not playing to avoid charges. `stop` deallocates the VM so you are not billed for compute.

**Monitor server uptime:**
```
python scripts/monitor.py
```

Checks every 60 seconds and logs uptime history to `server_log.txt`.

**Cleanup:**
```
az group delete --name vein-server-rg --yes
```

---

## Deploying on a New Azure Account

Anyone can clone this repo and deploy their own instance:
1. Create `config.json` with their own subscription ID
2. Run the build and deploy commands above

All infrastructure is reproducible from code — no manual Azure portal setup required.
