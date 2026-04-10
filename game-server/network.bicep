// network.bicep — Virtual Network and Subnet

param location string
param prefix string

resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: '${prefix}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: 'default'
        properties: {
          addressPrefix: '10.0.1.0/24'   // <-- this carves out the subnet
        }
      }
    ]
  }
}

// We need to output the subnet ID so the VM can attach to it later
output subnetId string = vnet.properties.subnets[0].id
