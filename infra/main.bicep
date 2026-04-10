// main.bicep — entry point for the Azure environment deployment
// Resources: Virtual Network, Storage Account, Linux VM

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Prefix used for naming all resources')
param prefix string = 'iac-demo'

@description('Admin username for the VM')
param adminUsername string = 'azureuser'

@description('Admin password for the VM')
@secure()
param adminPassword string

module network 'network.bicep' = {
  name:'networkDeployment'
  params: {
    location: location
    prefix: prefix
  }
}

module storage 'storage.bicep' = {
  name:'storageDeployment'
  params: {
    location: location
    prefix: prefix
  }
}

module vm 'vm.bicep' = {
  name:'vmDeployment'
  params: {
    location: location
    prefix: prefix
    adminUsername: adminUsername
    adminPassword: adminPassword
    subnetId: network.outputs.subnetId 
  }
}
