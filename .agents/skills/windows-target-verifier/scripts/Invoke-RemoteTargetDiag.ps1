<#
.SYNOPSIS
    Universal Deterministic Remote Execution & Diagnostics Harness for Windows Targets.
.DESCRIPTION
    Executes PowerShell diagnostic payloads and test suites across an OpenSSH boundary
    to Windows targets with 100% transport fidelity.
    
    Solves 3 major remote Windows automation pitfalls:
    1. Remote Quote Mangling: AST syntax validation + UTF-16LE Base64 encoding.
    2. Variable Expansion Collisions: Prevents host-side variable expansion.
    3. The Windows 8191 Command-Line Limit: Automatically switches from -EncodedCommand
       to SCP staging when payload size exceeds safe command line lengths.
.PARAMETER TargetHost
    IP address or hostname of the remote Windows target.
.PARAMETER Port
    SSH port on remote target (default: 22).
.PARAMETER User
    Remote username (default: $env:USERNAME).
.PARAMETER FilePath
    Local path to a PowerShell script to execute on the remote target.
.PARAMETER ScriptBlockText
    Raw scriptblock text string to execute.
.PARAMETER TempRemotePath
    Remote path for staged script execution when size exceeds command line threshold.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$TargetHost,

    [int]$Port = 22,

    [string]$User = $env:USERNAME,

    [string]$FilePath,

    [string]$ScriptBlockText,

    [string]$TempRemotePath = "C:/Users/$User/AppData/Local/Temp/RemoteDiag_Payload.ps1"
)

if ($FilePath) {
    if (-not (Test-Path $FilePath)) {
        throw "File not found: $FilePath"
    }
    $ScriptBlockText = Get-Content -Path $FilePath -Raw
}

if (-not $ScriptBlockText) {
    throw "Either -FilePath or -ScriptBlockText must be provided."
}

# 1. AST Syntax Pre-Validation (Host-side safety gate)
$parseErrors = $null
$tokens = $null
$null = [System.Management.Automation.Language.Parser]::ParseInput($ScriptBlockText, [ref]$tokens, [ref]$parseErrors)

if ($parseErrors.Count -gt 0) {
    throw "AST PARSE ERROR: Remote script contains syntax errors before transmission:`n$($parseErrors | Out-String)"
}

# 2. Threshold-Based Transport Selection
$bytes = [System.Text.Encoding]::Unicode.GetBytes($ScriptBlockText)
$encoded = [Convert]::ToBase64String($bytes)

if ($encoded.Length -le 6000) {
    # Direct Base64 Execution (-EncodedCommand)
    & ssh -p $Port -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$User@$TargetHost" "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand $encoded"
} else {
    # Large Payload SCP Staging & File Execution
    $tempFile = if ($FilePath) { $FilePath } else {
        $t = [System.IO.Path]::GetTempFileName() + ".ps1"
        Set-Content -Path $t -Value $ScriptBlockText -Encoding UTF8
        $t
    }
    
    & scp -P $Port -o BatchMode=yes -o StrictHostKeyChecking=accept-new $tempFile "$User@$TargetHost`:$TempRemotePath"
    if ($LASTEXITCODE -ne 0) {
        throw "SCP transport failed while staging payload to $TargetHost."
    }
    
    & ssh -p $Port -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$User@$TargetHost" "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$TempRemotePath`""
}
