// shared/server.bicep — reusable game server module
// All game-specific values are passed in as params

param location string
param prefix string
param adminUsername string

@secure()
param adminPassword string

param subnetId string
param vmSize string
param gamePort string
param queryPort string
param cloudInitContent string   // base64 encoded cloud-init, passed in from main.bicep

resource publicIP 'Microsoft.Network/publicIPAddresses@2023-04-01' = {
  name: '${prefix}-pip'
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: '${prefix}-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-game-port'
        properties: {
          priority: 100
          protocol: 'Udp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: gamePort   // dynamic — set per game
        }
      }
      {
        name: 'allow-query-port'
        properties: {
          priority: 110
          protocol: 'Udp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: queryPort  // dynamic — set per game
        }
      }
      {
        name: 'allow-ssh'
        properties: {
          priority: 120
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
    ]
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2023-04-01' = {
  name: '${prefix}-nic'
  location: location
  properties: {
    networkSecurityGroup: {
      id: nsg.id
    }
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: subnetId
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: '${prefix}-vm'
  location: location
  zones: ['1']
  properties: {
    hardwareProfile: {
      vmSize: vmSize   // dynamic — set per game
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        diskSizeGB: 64
        managedDisk: {
          storageAccountType: 'StandardSSD_LRS'
        }
      }
    }
    osProfile: {
      computerName: '${prefix}-vm'
      adminUsername: adminUsername
      adminPassword: adminPassword
      customData: cloudInitContent   // dynamic — passed in from each game's main.bicep
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
  }
}

output serverIP string = publicIP.properties.ipAddress
