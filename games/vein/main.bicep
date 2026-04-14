@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Prefix used for naming all resources')
param prefix string = 'vein-server'

@description('Admin username for the VM')
param adminUsername string = 'azureuser'

@description('Admin password for the VM')
@secure()
param adminPassword string

module network '../shared/network.bicep' = {
  name: 'networkDeployment'
  params: {
    location: location
    prefix: prefix
  }
}

module server '../shared/server.bicep' = {
  name: 'serverDeployment'
  params: {
    location: location
    prefix: prefix
    adminUsername: adminUsername
    adminPassword: adminPassword
    subnetId: network.outputs.subnetId
  }
}
