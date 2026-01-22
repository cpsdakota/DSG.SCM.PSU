#requires -Version 7.1
Set-StrictMode -Version Latest

# -----------------------------
# Script-scope token cache
# -----------------------------
$script:ScmTokenCache = [ordered]@{
    AccessToken = $null
    ExpiresAt   = $null   # [DateTime]
    TsgId       = $null
    ClientId    = $null
}

function Get-SCMAccessToken {
<#
.SYNOPSIS
Gets an OAuth access token for Strata Cloud Manager (SCM) using client credentials.

.DESCRIPTION
Requests an access token from the Palo Alto auth endpoint using the OAuth2
client_credentials grant. Optionally returns a cached token if it is still valid.

.PARAMETER TsgId
Tenant Service Group (TSG) ID.

.PARAMETER ClientId
OAuth Client ID from an SCM Service Account.

.PARAMETER ClientSecret
OAuth Client Secret from an SCM Service Account.

.PARAMETER ForceRefresh
Forces retrieval of a new token even if a cached token exists.

.OUTPUTS
System.String (access token)

.EXAMPLE
$token = Get-SCMAccessToken -TsgId "1793197006" -ClientId "Lab-API@..." -ClientSecret "..."
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TsgId,

        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [switch]$ForceRefresh
    )

    try {
        # Return cached token if still valid for at least 60 seconds
        if (-not $ForceRefresh) {
            $cacheOk =
                $script:ScmTokenCache.AccessToken -and
                $script:ScmTokenCache.ExpiresAt -and
                ([DateTime]::UtcNow.AddSeconds(60) -lt $script:ScmTokenCache.ExpiresAt) -and
                ($script:ScmTokenCache.TsgId -eq $TsgId) -and
                ($script:ScmTokenCache.ClientId -eq $ClientId)

            if ($cacheOk) {
                return $script:ScmTokenCache.AccessToken
            }
        }

        $tokenUri = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

        $basicAuth = [Convert]::ToBase64String(
            [Text.Encoding]::ASCII.GetBytes("$($ClientId):$($ClientSecret)")
        )

        $tokenResponse = Invoke-RestMethod -Method Post `
            -Uri $tokenUri `
            -Headers @{ Authorization = "Basic $($basicAuth)" } `
            -ContentType "application/x-www-form-urlencoded" `
            -Body "grant_type=client_credentials&scope=tsg_id:$($TsgId)"

        if (-not $tokenResponse.access_token) {
            throw "OAuth token was not returned (no access_token field)."
        }

        # expires_in is seconds (usually 900)
        $expiresIn = 900
        if ($tokenResponse.expires_in) { $expiresIn = [int]$tokenResponse.expires_in }

        $script:ScmTokenCache.AccessToken = $tokenResponse.access_token
        $script:ScmTokenCache.ExpiresAt   = [DateTime]::UtcNow.AddSeconds($expiresIn)
        $script:ScmTokenCache.TsgId       = $TsgId
        $script:ScmTokenCache.ClientId    = $ClientId

        return $tokenResponse.access_token
    }
    catch {
        throw "Get-SCMAccessToken failed: $($_.Exception.Message)"
    }
}

function Invoke-SCMRequest {
<#
.SYNOPSIS
Invokes a Strata Cloud Manager (SCM) REST request.

.DESCRIPTION
Obtains an OAuth token (cached when possible) and calls an SCM API endpoint.
Supports GET/POST/PUT/PATCH/DELETE and optional JSON body.

.PARAMETER Method
HTTP method.

.PARAMETER Uri
Full endpoint URL.

.PARAMETER TsgId
Tenant Service Group (TSG) ID.

.PARAMETER ClientId
OAuth Client ID.

.PARAMETER ClientSecret
OAuth Client Secret.

.PARAMETER Body
Optional request body object. Will be JSON-serialized.

.PARAMETER ReturnRaw
Return the raw response instead of parsed JSON (rarely needed).

.OUTPUTS
System.Object

.EXAMPLE
Invoke-SCMRequest -Method GET -Uri "https://api.strata.paloaltonetworks.com/config/setup/v1/folders" -TsgId "..." -ClientId "..." -ClientSecret "..."
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('GET','POST','PUT','PATCH','DELETE')]
        [string]$Method,

        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$TsgId,

        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory=$false)]
        [object]$Body,

        [switch]$ReturnRaw
    )

    try {
        $token = Get-SCMAccessToken -TsgId $TsgId -ClientId $ClientId -ClientSecret $ClientSecret

        $headers = @{
            Authorization = "Bearer $($token)"
            Accept        = "application/json"
        }

        $irmParams = @{
            Method  = $Method
            Uri     = $Uri
            Headers = $headers
        }

        if ($PSBoundParameters.ContainsKey('Body')) {
            $headers["Content-Type"] = "application/json"
            $irmParams.Body = ($Body | ConvertTo-Json -Depth 50)
        }

        if ($ReturnRaw) {
            $irmParams.Add("ResponseHeadersVariable", "rh")
            return Invoke-WebRequest @irmParams
        }

        return Invoke-RestMethod @irmParams
    }
    catch {
        throw "Invoke-SCMRequest failed for $($Method) $($Uri): $($_.Exception.Message)"
    }
}

function Get-SCMFolders {
<#
.SYNOPSIS
Retrieves folder and device hierarchy from Strata Cloud Manager (SCM).

.DESCRIPTION
Queries the SCM Folders API and returns all folders/containers and any devices
associated to those folders for the specified tenant (TSG).

.PARAMETER TsgId
Tenant Service Group (TSG) ID.

.PARAMETER ClientId
OAuth Client ID from the SCM Service Account.

.PARAMETER ClientSecret
OAuth Client Secret from the SCM Service Account.

.OUTPUTS
System.Object (has a .data collection)

.EXAMPLE
$folders = Get-SCMFolders -TsgId "1793197006" -ClientId "Lab-API@..." -ClientSecret "..."
$folders.data | ft

.NOTES
Uses token caching via Get-SCMAccessToken.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TsgId,

        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret
    )

    $uri = "https://api.strata.paloaltonetworks.com/config/setup/v1/folders"

    Invoke-SCMRequest -Method GET -Uri $uri -TsgId $TsgId -ClientId $ClientId -ClientSecret $ClientSecret
}

Export-ModuleMember -Function `
    Get-SCMAccessToken, `
    Invoke-SCMRequest, `
    Get-SCMFolders
