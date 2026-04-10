// vm.bicep — Network Interface + Linux VM

param location string
param prefix string
param adminUsername string

@secure()
param adminPassword string

param subnetId string   // passed in from main.bicep via the network module output

resource nic 'Microsoft.Network/networkInterfaces@2023-04-01' = {
  name: '${prefix}-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: subnetId   // this is how the NIC attaches to our subnet
          }
          privateIPAllocationMethod: 'Dynamic'  // Azure assigns the IP automatically
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
      vmSize: 'Standard_D2as_v7'   // smallest/cheapest VM — 1 CPU, 1GB RAM
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
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
    }
    osProfile: {
      computerName: '${prefix}-vm'
      adminUsername: adminUsername
      adminPassword: adminPassword
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

output vmId string = vm.id
