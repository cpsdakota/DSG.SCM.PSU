```powershell

Import-Module DSG.SCM -force

# if the module isn't installed where powershell looks, replace with the file path of the .psm1 use below as an example
# Import-Module C:\Users\someuser\Documents\someuserRepo\DSG.SCM.PSU\DSG.SCM\DSG.SCM.psm1 -force

Get-Help Get-SCMFolders -Examples
Get-Help Invoke-SCMRequest -Examples
Get-Help Get-SCMAccessToken -Examples

NAME
    Get-SCMFolders

SYNOPSIS
    Retrieves folder and device hierarchy from Strata Cloud Manager (SCM).


    -------------------------- EXAMPLE 1 --------------------------

    PS > $folders = Get-SCMFolders -TsgId "1793197006" -ClientId "Lab-API@..." -ClientSecret "..."
    $folders.data | ft

#########################################
NAME
    Invoke-SCMRequest

SYNOPSIS
    Invokes a Strata Cloud Manager (SCM) REST request.


    -------------------------- EXAMPLE 1 --------------------------

    PS > Invoke-SCMRequest -Method GET -Uri "https://api.strata.paloaltonetworks.com/config/setup/v1/folders" -TsgId "..." -ClientId "..." -ClientSecret "..."

#############################################
NAME
    Get-SCMAccessToken

SYNOPSIS
    Gets an OAuth access token for Strata Cloud Manager (SCM) using client credentials.


    -------------------------- EXAMPLE 1 --------------------------

    PS > $token = Get-SCMAccessToken -TsgId "1793197006" -ClientId "Lab-API@..." -ClientSecret "..."

```