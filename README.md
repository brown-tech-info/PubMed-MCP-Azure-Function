
# PubMed MCP Azure Function

This project is a Python-based MCP (Model Context Protocol) server for PubMed, hosted as an Azure Function and integrated with Azure AI Foundry.

## Features
- Search PubMed articles and return titles and abstracts via HTTP requests.
- Uses PubMed Entrez API with API key and email for authentication.
- Deployed on Azure Functions (Linux, Python 3.11).
- Anonymous public endpoint (no function key required).
- OpenAPI 3.0.1 specification for agent/tool integration.

## Setup

### Prerequisites
- Python 3.11
- Azure Functions Core Tools
- Azure CLI
- An Azure subscription
- PubMed API key and registered email

### Local Development
1. Clone the repository.
2. Install dependencies:
   ```pwsh
   pip install -r requirements.txt
   ```
3. Add your PubMed API key and email to `local.settings.json`:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "PUBMED_API_KEY": "<your_pubmed_api_key>",
       "PUBMED_EMAIL": "<your_email>"
     }
   }
   ```
4. Start the function locally:
   ```pwsh
   func start
   ```
5. Test locally:
   ```pwsh
   curl "http://localhost:7071/api/pubmed_mcp?query=cancer"
   ```

### Azure Deployment
1. Log in to Azure:
   ```pwsh
   az login
   ```
2. Create a resource group:
   ```pwsh
   az group create --name <ResourceGroup> --location <Region>
   ```
3. Create a storage account:
   ```pwsh
   az storage account create --name <StorageAccount> --location <Region> --resource-group <ResourceGroup> --sku Standard_LRS
   ```
4. Create a Function App (Linux, Python 3.11):
   ```pwsh
   az functionapp create --resource-group <ResourceGroup> --consumption-plan-location <Region> --runtime python --runtime-version 3.11 --functions-version 4 --name <FunctionAppName> --storage-account <StorageAccount> --os-type Linux
   ```
5. Publish your code:
   ```pwsh
   func azure functionapp publish <FunctionAppName>
   ```
6. Set environment variables in Azure:
   ```pwsh
   az functionapp config appsettings set --name <FunctionAppName> --resource-group <ResourceGroup> --settings PUBMED_API_KEY="<your_pubmed_api_key>" PUBMED_EMAIL="<your_email>"
   ```
7. Test the deployed function (no key required):
   ```pwsh
   curl "https://<FunctionAppName>.azurewebsites.net/api/pubmed_mcp?query=cancer"
   ```

## Agent & Tool Integration
- The function is compatible with Azure AI Foundry agents and other OpenAPI-based tools.
- The OpenAPI spec (`openapi.json`) describes the endpoint for agent integration.
- Example agent prompt:
  > Find recent PubMed articles about cancer and return their titles and abstracts.

## Security
- **Do not commit your real API keys or sensitive information to source control.**
- Use environment variables for secrets.

## Logging
- The function logs requests, errors, and PubMed API responses to the Azure log stream.

## Customization
- You can extend the MCP server to support more PubMed features or custom endpoints.

## License
MIT
