# Azure IaC Deployment Automation

Deploys a multi-resource Azure environment using modular Bicep templates, automated with a Python script.

## Resources Deployed

- Virtual Network + Subnet
- Storage Account
- Linux VM (Ubuntu 22.04) with Network Interface

## Project Structure

```
├── infra/
│   ├── main.bicep       # Entry point, wires all modules together
│   ├── network.bicep    # Virtual Network + Subnet
│   ├── storage.bicep    # Storage Account
│   └── vm.bicep         # Network Interface + Linux VM
├── scripts/
│   └── deploy.py        # Automates deployment, logging, and budget alerts
└── config.json          # Your subscription settings (not committed)
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

4. Build the Bicep template:

```
az bicep build --file infra/main.bicep --outfile infra/main.json
```

5. Run the deployment script:

```
python scripts/deploy.py
```

The script will prompt for your email (for budget alerts) and a VM admin password, then deploy all resources and log what was created.

## Cleanup

Delete all resources when done to avoid charges:

```
az group delete --name iac-demo-rg --yes
```
