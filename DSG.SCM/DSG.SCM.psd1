@{
    RootModule        = 'DSG.SCM.psm1'
    ModuleVersion     = '0.1.0'
    GUID              = 'b7d8c4d3-2f8b-4b5a-9f8a-6f37b7f2b8c1'
    Author            = 'Chuck Schaffold'
    CompanyName       = 'DSG'
    Copyright         = '(c) DSG. All rights reserved.'
    Description       = 'PowerShell helpers for Palo Alto Strata Cloud Manager (SCM) APIs (token + request wrapper + folders).'

    PowerShellVersion = '5.1'

    FunctionsToExport = @('Get-SCMAccessToken','Invoke-SCMRequest','Get-SCMFolders')
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()

    PrivateData = @{
        PSData = @{
            Tags       = @('PaloAlto','SCM','StrataCloudManager','API','OAuth')
            ProjectUri = ''
        }
    }
}
