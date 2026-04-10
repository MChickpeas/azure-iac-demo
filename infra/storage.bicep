// storage.bicep — Storage Account

param location string
param prefix string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${replace(prefix, '-', '')}stor'
  location: location
  sku: {name: 'Standard_LRS'} //locally redundant — cheapest, fine for dev
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

output storageId string = storageAccount.id
