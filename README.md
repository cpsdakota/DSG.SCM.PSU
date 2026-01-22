
```powershell

Import-Module DSG.SCM -force

# if the module isn't installed where powershell looks, replace with the file path of the .psm1 use below as an example
# Import-Module C:\Users\someuser\Documents\someuserRepo\DSG.SCM.PSU\DSG.SCM\DSG.SCM.psm1 -force



$tsgId        =  "1793197006"
$clientId     =  "Lab-API@1793197006.iam.panserviceaccount.com"
$clientSecret =  "e031af04-1a58-4d31-b04b-4a01154e9345"

# The following was from a lab now destroyed

$folders = Get-SCMFolders `
  -TsgId        $tsgId `
  -ClientId     $clientId `
  -ClientSecret $clientSecret

$folders.data | ft

device_only display_name                id                                   model name                        parent                 serial_number   type
----------- ------------                --                                   ----- ----                        ------                 -------------   ----
       True GFW-PodX-1                  fc87d8dc-4a10-4dad-8561-5e3fa71b901b PA-VM 007958000766226             PodX-Remote-Branch     007958000766226 on-prem
       True GFW-PodX-2                  17eba9c3-c89a-4982-b0a0-c49e16f753b5 PA-VM 007958000766239             PodX-Remote-Branch     007958000766239 on-prem
                                        571356e6-24a7-440b-858b-486e8ae7c383       PodX-Remote-Branch          Remote Branches                        container
                                        94233490-ce8e-46f0-89b3-e617dc28fd0b       Remote Branches             ngfw-shared                            container
                                        be493a1a-21be-4a4a-a549-5559f69e4235       ngfw-shared                 All                                    container
            Mobile Users                c9b2d0f3-26f5-4c07-aad5-4539fac22e9f       Mobile Users                Mobile Users Container                 cloud
            Mobile Users Explicit Proxy 5c4a1d0e-73f1-41b1-9b04-83bed740a652       Mobile Users Explicit Proxy Mobile Users Container                 cloud
                                        672bf030-29fc-4499-a7f7-3277d5f3e9ce       Mobile Users Container      Prisma Access                          container
            Colo Connect                8ecb65d3-4f79-4202-bd25-27b793f62168       Colo Connect                Prisma Access                          cloud
            Remote Networks             5b191ea5-fed9-46af-8c12-a4e2967cf809       Remote Networks             Prisma Access                          cloud
            Service Connections         3a93e6fb-9465-4138-9c49-767f93620ff8       Service Connections         Prisma Access                          cloud
                                        a70b17ba-4aee-4096-8b64-62753e25673a       Prisma Access               All                                    container
            Global                      62d00570-c4ca-4683-a12e-08b4b9f5a663       All                                                                container
```

```powershell

$folders.data | ConvertTo-Json -Depth 10

```

```json

[
  {
    "device_only": true,
    "display_name": "GFW-PodX-1",
    "id": "fc87d8dc-4a10-4dad-8561-5e3fa71b901b",
    "model": "PA-VM",
    "name": "007958000766226",
    "parent": "PodX-Remote-Branch",
    "serial_number": "007958000766226",
    "type": "on-prem"
  },
  {
    "device_only": true,
    "display_name": "GFW-PodX-2",
    "id": "17eba9c3-c89a-4982-b0a0-c49e16f753b5",
    "model": "PA-VM",
    "name": "007958000766239",
    "parent": "PodX-Remote-Branch",
    "serial_number": "007958000766239",
    "type": "on-prem"
  },
  {
    "id": "571356e6-24a7-440b-858b-486e8ae7c383",
    "name": "PodX-Remote-Branch",
    "parent": "Remote Branches",
    "type": "container"
  },
  {
    "id": "94233490-ce8e-46f0-89b3-e617dc28fd0b",
    "name": "Remote Branches",
    "parent": "ngfw-shared",
    "type": "container"
  },
  {
    "id": "be493a1a-21be-4a4a-a549-5559f69e4235",
    "name": "ngfw-shared",
    "parent": "All",
    "snippets": [
      "Auto-VPN-Default-Snippet"
    ],
    "type": "container"
  },
  {
    "display_name": "Mobile Users",
    "id": "c9b2d0f3-26f5-4c07-aad5-4539fac22e9f",
    "name": "Mobile Users",
    "parent": "Mobile Users Container",
    "type": "cloud"
  },
  {
    "display_name": "Mobile Users Explicit Proxy",
    "id": "5c4a1d0e-73f1-41b1-9b04-83bed740a652",
    "name": "Mobile Users Explicit Proxy",
    "parent": "Mobile Users Container",
    "snippets": [
      "proxy"
    ],
    "type": "cloud"
  },
  {
    "id": "672bf030-29fc-4499-a7f7-3277d5f3e9ce",
    "name": "Mobile Users Container",
    "parent": "Prisma Access",
    "type": "container"
  },
  {
    "display_name": "Colo Connect",
    "id": "8ecb65d3-4f79-4202-bd25-27b793f62168",
    "name": "Colo Connect",
    "parent": "Prisma Access",
    "type": "cloud"
  },
  {
    "display_name": "Remote Networks",
    "id": "5b191ea5-fed9-46af-8c12-a4e2967cf809",
    "name": "Remote Networks",
    "parent": "Prisma Access",
    "type": "cloud"
  },
  {
    "display_name": "Service Connections",
    "id": "3a93e6fb-9465-4138-9c49-767f93620ff8",
    "name": "Service Connections",
    "parent": "Prisma Access",
    "type": "cloud"
  },
  {
    "id": "a70b17ba-4aee-4096-8b64-62753e25673a",
    "name": "Prisma Access",
    "parent": "All",
    "snippets": [
      "optional-default",
      "office365",
      "rbi",
      "saas-tenant-restrictions"
    ],
    "type": "container"
  },
  {
    "display_name": "Global",
    "id": "62d00570-c4ca-4683-a12e-08b4b9f5a663",
    "name": "All",
    "parent": "",
    "snippets": [
      "default",
      "Web-Security-Default",
      "hip-default",
      "dlp-predefined-snippet"
    ],
    "type": "container"
  }
]
