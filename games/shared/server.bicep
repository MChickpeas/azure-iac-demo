// server.bicep - VEIN Game server : Public IP, Firewall, VM

param location string
param prefix string
param adminUsername string

@secure()
param adminPassword string

param subnetId string

resource publicIP 'Microsoft.Network/publicIPAddresses@2023-04-01' = {
  name:'${prefix}-pip'
  location: location
  sku: {name:'Standard'}
  properties:{
    publicIPAllocationMethod:'Static'
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: '${prefix}-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-vein-game'
        properties: {
          priority: 100
          protocol: 'Udp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '7777'
        }
      }
      {
        name: 'allow-steam-query'
        properties: {
          priority: 110
          protocol: 'Udp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '27015'
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
      id: nsg.id     // attach the firewall rules to this NIC
    }
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: subnetId
          }
          privateIPAllocationMethod: 'Dynamic'  // private IP is fine as dynamic
          publicIPAddress: {
            id: publicIP.id  // attach the public IP so players can reach the server
          }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: '${prefix}-vm'
  location: location
  zones:['1']
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_DC4ds_v3'
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'       // Ubuntu 22.04 LTS
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
      customData: loadFileAsBase64('cloud-init.yml')  // runs on first boot
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id    // attaches the NIC we defined above
        }
      ]
    }
  }
}


output serverIP string = publicIP.properties.ipAddress
