<#
.SYNOPSIS
    Get real network adapter IP address, excluding virtual adapters

.DESCRIPTION
    This script detects and gets the IP address of real network adapters,
    distinguishing between physical and virtual adapters, prioritizing
    physical adapter IPv4 addresses. Outputs JSON format for Python parsing.

.NOTES
    Execution Policy: RemoteSigned or Unrestricted
    Command: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

Add-Type -AssemblyName System.Web

function Get-RealIPAddress {
    try {
        $adapters = Get-NetAdapter -Physical | Where-Object { 
            $_.Status -eq 'Up' -and 
            $_.InterfaceDescription -notlike '*Virtual*' -and
            $_.InterfaceDescription -notlike '*VMware*' -and
            $_.InterfaceDescription -notlike '*VirtualBox*' -and
            $_.InterfaceDescription -notlike '*Hyper-V*' -and
            $_.Name -notlike '*vEthernet*' -and
            $_.Name -notlike '*WSL*'
        } | Sort-Object -Property LinkSpeed -Descending

        if ($adapters) {
            $primaryAdapter = $adapters[0]
            $ipConfig = Get-NetIPAddress -InterfaceIndex $primaryAdapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            
            if ($ipConfig) {
                $result = @{
                    success = $true
                    ip = $ipConfig.IPAddress
                    adapter = $primaryAdapter.Name
                    description = $primaryAdapter.InterfaceDescription
                    mac = $primaryAdapter.MacAddress
                    message = "Successfully obtained real IP address"
                }
            }
            else {
                $result = @{
                    success = $false
                    ip = $null
                    adapter = $null
                    description = $null
                    mac = $null
                    message = "Physical adapter has no IPv4 address assigned"
                }
            }
        }
        else {
            $fallbackAdapters = Get-NetAdapter | Where-Object { 
                $_.Status -eq 'Up' -and 
                $_.InterfaceDescription -notlike '*Loopback*'
            } | Sort-Object -Property LinkSpeed -Descending
            
            if ($fallbackAdapters) {
                $fallbackAdapter = $fallbackAdapters[0]
                $fallbackIpConfig = Get-NetIPAddress -InterfaceIndex $fallbackAdapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
                
                if ($fallbackIpConfig) {
                    $result = @{
                        success = $true
                        ip = $fallbackIpConfig.IPAddress
                        adapter = $fallbackAdapter.Name
                        description = $fallbackAdapter.InterfaceDescription
                        mac = $fallbackAdapter.MacAddress
                        message = "Using fallback adapter to get IP address"
                    }
                }
                else {
                    $result = @{
                        success = $false
                        ip = $null
                        adapter = $null
                        description = $null
                        mac = $null
                        message = "No available network adapter found"
                    }
                }
            }
            else {
                $result = @{
                    success = $false
                    ip = $null
                    adapter = $null
                    description = $null
                    mac = $null
                    message = "No active network adapter found"
                }
            }
        }
    }
    catch {
        $result = @{
            success = $false
            ip = $null
            adapter = $null
            description = $null
            mac = $null
            message = "Error getting IP address: $($_.Exception.Message)"
        }
    }
    
    return $result | ConvertTo-Json -Depth 3
}

$result = Get-RealIPAddress
[System.Console]::WriteLine($result)
