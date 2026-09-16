# Windows Target Environment Deterministic State Verification & Operational Testing Engine
## Air-Gapped Universal Architectural Specification

> **Classification**: Antigravity Skill Definition & Operational Governance Architecture  
> **Engine Scope**: Universal Windows Target Verification Engine (Zero Domain/Host Hardcoding)  
> **Governing Standards**: Deterministic Verification, Multi-Tier Empirical Assertions, Zero-Hallucination Guardrails, Management Host Isolation, Lifecycle Invariance.  
> **Target Applicability**: Any physical, virtual, or containerized Windows environment (Client/Server, Windows 10/11, Home/Pro/Enterprise, LTSC).

---

## Executive Overview & Architectural Philosophy

When managing or automating Windows operating systems, artificial intelligence agents and human engineers frequently suffer from **superficial verification failure**:
1. **The Write-Assumption Fallacy**: Assuming that because a `Set-ItemProperty`, `New-Item`, or CLI command completed with exit code 0, the desired setting is actually in effect.
2. **The Edition Ignorance Trap**: Attempting to set Group Policies, AppLocker rules, or CSP flags on Windows Home editions that silently ignore them.
3. **The Transient State Illusion**: Verifying a setting immediately after applying it, only for the setting to revert upon process exit, user logoff, or reboot due to internal application config flushes.
4. **The Host Bleed Disaster**: Running queries or modifications on the *management workstation* rather than the designated *target node*, polluting the administrator's primary machine.
5. **The Shallow Test Trap**: Writing naive, surface-level queries (e.g. `Get-Item C:\hiberfil.sys`) that break against kernel-locked, Hidden+System files, producing false negatives.

This engine enforces a **100% deterministic, empirical, multi-tiered verification standard** for every system state change. Nothing is considered complete until verified against active runtime behavior, lifecycle invariance, and regression boundaries.

---

## The 4 Tiers of Empirical Verification

Every system setting, policy, or operational change must be categorized and proven against the **4 Tiers of Empirical Verification**:

```
+-------------------------------------------------------------------------------------------------------+
|                                THE 4 TIERS OF EMPIRICAL VERIFICATION                                  |
+----------------------+--------------------------------------------------------------------------------+
| Tier 1: Syntactic    | Passive read-back of storage state (Registry key exists, JSON edited,          |
|                      | cmdlet returned 0). Status: Necessary prerequisite, but ZERO proof of impact. |
|----------------------+--------------------------------------------------------------------------------|
| Tier 2: Behavioral   | Active runtime proof (Service throws Error 1058 on start; network socket drops |
|                      | or accepts traffic; application policy engine reports Status: OK/Active).      |
|----------------------+--------------------------------------------------------------------------------|
| Tier 3: Invariant    | Lifecycle persistence (Setting survives application restart, user session     |
|                      | logoff, system reboot, and application-internal config manager flushes).       |
|----------------------+--------------------------------------------------------------------------------|
| Tier 4: Regression   | Cross-setting blast radius validation (Executing Step N MUST NOT break any     |
|                      | invariant established in Steps 1 through N-1. Full suite must re-run).         |
+----------------------+--------------------------------------------------------------------------------+
```

> [!CRITICAL]
> **The Hallucination Detection Rule**: If an agent cannot formulate an executable Tier 2 (Behavioral) or Tier 3 (Invariant) test for a requested modification (because the application or OS edition provides no mechanism, policy schema, or API to control that behavior), the agent **MUST NOT** fabricate registry keys or configuration files and claim success.
> The agent must halt, inform the user that the setting is *empirically unverifiable and unsupported by the software runtime*, and propose a proven architectural alternative.

---

## Universal Configuration Item (CI) Verification Taxonomy

Whenever an agent touches a system, it must identify the CI type and execute the corresponding empirical verification standard:

```
+-------------------------------------------------------------------------------------------------------+
|                             UNIVERSAL WINDOWS CONFIGURATION ITEM (CI) MATRIX                          |
+-------------------+------------------------------------+----------------------------------------------+
| CI Type           | Authoritative Query Mechanism      | Mandatory Tier 2 Behavioral Test Standard     |
+-------------------+------------------------------------+----------------------------------------------+
| 1. OS Service     | Get-Service / Win32_Service / sc   | Active start/stop probe; assert exit/error   |
| 2. Registry Policy| HKLM/HKCU via Get-ItemProperty     | Query application policy engine or runtime   |
| 3. Network/Socket | Get-NetTCPConnection / PortFilter  | Active TCP/UDP socket probe via loopback/LAN |
| 4. Storage/Volume | Get-Disk / Get-Partition / Volume  | File read/write throughput & mount validation|
| 5. Hardware/Device| Get-PnpDevice / Win32_PnPEntity    | Device status 'OK' & driver loaded in kernel |
| 6. Environment/Var| [Environment]::GetEnvironmentVar   | Process spawn inheriting altered env variable|
| 7. App Deployment | Win32_Product / AppX / Package     | Process execution test & binary checksum     |
| 8. Scheduled Task | Get-ScheduledTask / TaskInfo       | Dry-run trigger check & exit code validation |
| 9. ACL / Security | icacls / Get-Acl                   | Non-admin access attempt (assert denied)     |
+-------------------+------------------------------------+----------------------------------------------+
```

---

## Universal Operational Directives

### Directive 0: Target Environment Binding & Management Host Isolation (The Zero-Host-Interference Rule)
The machine running the agent/IDE session is the **Management Workstation**, NOT the target environment, unless the user explicitly declares the local machine to be the target.
- **Strict Prohibition Against Host Probing**: When an instruction, plan, or task concerns an external target, the agent is **STRICTLY FORBIDDEN** from running diagnostic commands, registry queries, CIM/WMI interrogations, or test scripts against the local management workstation.
- **Transport Binding Mandate**: All operational commands for an external target MUST be explicitly wrapped in the designated remote transport channel (`ssh user@target ...`, `Invoke-Command -ComputerName target ...`, or PSSession).

---

### Directive 0.1: Pre-Execution Plan-Only Invariant & Interactive Execution Gating
When the conversation, mode, or prompt indicates planning, strategy, or pre-flight design:
1. **Strict Plan-Only Boundary**: Zero operational commands may be executed against ANY machine (host, target, or network nodes).
2. **Explicit User Approval Gate**: No test suite, diagnostic query, or configuration change may be initiated until the user explicitly signals authorization.

---

### Directive 0.2: The Base64 Remote Transport Invariant (`-EncodedCommand`)
When transmitting PowerShell script blocks across OpenSSH or remote CLI transports:
1. **Banned**: Fragile nested string quoting (`ssh host "powershell -Command \"...\""`).
2. **Mandatory**: Pre-encode all remote payloads into UTF-16LE Base64 strings and execute via `powershell -NoProfile -NonInteractive -EncodedCommand <Base64>`.

---

### Directive 0.3: Pre-Execution Target Environment Disambiguation
When an operational landscape comprises multiple machines (e.g. Workstation, Student Laptop, Gaming PC), the agent must maintain strict, unambiguous separation across:
1. **Target Identification**: Hostname, IP address, OS build, and user credentials must be explicitly tracked per machine. Never conflate specifications, test scripts, or command targets.
2. **Dedicated Test Suites**: Every physical machine must have its own dedicated test suite.
3. **Mandatory Script-Level Hostname Assertion**: Every executable script or Pester test suite intended for an external target MUST include an unbypassable hostname check at Line 1 (`Assert-TargetEnvironmentIdentity`).

---

### Directive 0.4: Empirical Test Construction & Anti-Hallucination Anchor Standard
A test framework is only as good as the quality of its test definitions. Naive, surface-level assertions generate false negatives and false positives. Every test definition must be anchored in verified operating system subsystem architecture, traceable to authoritative sources, and strictly adhere to these rules:

1. **Mandatory Subsystem Authority Interrogation (Never Rely on Fragile Surface Probing)**:
   - *Power & Sleep*: Always interrogate the kernel power authority (`powercfg /qh` and `powercfg /a`). Windows 11 hides settings like `LIDACTION` from standard `/q` queries. Never rely on superficial GUI inspection or fragile file lookups.
   - *Storage & Recovery*: Interrogate `Get-Disk`, partition GPT type GUIDs (`{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}` for ESP), and `reagentc /info`. Never rely on drive letters alone.
   - *Services & Policies*: Interrogate `Get-Service`, registry `Start = 4`, and execute an active start probe to assert `Error 1058`.
2. **Protected System Artifact Rule (The Root File Invariant)**:
   - Root-level Windows system files (`hiberfil.sys`, `pagefile.sys`, `swapfile.sys`, `Recovery\Winre.wim`) possess protected kernel attributes: `Hidden + System + Kernel Lock`.
   - **BANNED**: Using `Get-Item` or `Test-Path` on root system artifacts (which silently fails or drops system files).
   - **MANDATORY**: Use either low-level .NET `[System.IO.File]::Exists()`, `New-Object System.IO.FileInfo()`, or `Get-ChildItem -Force -Hidden -System`.
3. **The Multi-Witness Incongruity Gate (Anti-False-Negative)**:
   - Every verification must cross-correlate **Witness 1 (Configuration Intent / Registry)** against **Witness 2 (Subsystem Kernel Authority)** against **Witness 3 (Physical Artifact)**.
   - If Intent and Subsystem Authority confirm a feature is active, but an artifact query returns false, the test engine must **NEVER** emit a silent `$false`. It must throw a `TEST_FRAMEWORK_INCONGRUITY` exception indicating the test's artifact probe is obstructed or flawed.

---

### Directive 1: The 5-Stage Operational Verification Loop
Whenever modifying any service, policy, storage, security, network, or application setting:
`[1. Pre-Flight Audit] -> [2. Idempotent Execution] -> [3. Syntactic Read-Back] -> [4. Behavioral Live Proof] -> [5. Cumulative Regression Run]`

---

## Universal Automated Verification Library

### 1. Universal Service Lockdown Assertion (Tiers 1 & 2)
```powershell
function Assert-ServiceLockdown {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$ServiceName)

    $svc = Get-Service -Name $ServiceName -ErrorAction Stop
    $regStart = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\$ServiceName" -ErrorAction Stop).Start
    
    if ($svc.StartType -ne "Disabled" -or $regStart -ne 4) {
        throw "Tier 1 Failed: Service '$ServiceName' is not disabled in Service Manager or Registry (Start = $regStart)."
    }
    
    try {
        Start-Service -Name $ServiceName -ErrorAction Stop
        throw "Tier 2 Failed: Service '$ServiceName' started successfully despite being marked disabled! Lockdown failed."
    } catch [System.InvalidOperationException] {
        Write-Host "  [PASS] Service '$ServiceName' is deterministically locked down and threw Error 1058 on start." -ForegroundColor Green
    }
}
```

### 2. Universal Port & Socket Assertion (Tier 2 - Sub-Second .NET Socket Engine)
```powershell
function Assert-PortListening {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][int]$Port,
        [string]$ComputerName = "127.0.0.1",
        [int]$TimeoutMs = 1000
    )

    # Sub-second low-level socket probe (avoids the 21-second Test-NetConnection ICMP/TCP retry hang)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $iar = $client.BeginConnect($ComputerName, $Port, $null, $null)
        $connected = $iar.AsyncWaitHandle.WaitOne($TimeoutMs)
        if (-not $connected) {
            throw "Tier 2 Failed: Port $Port on $ComputerName did not respond within ${TimeoutMs}ms (Closed or Filtered)."
        }
        $client.EndConnect($iar)
        Write-Host "  [PASS] Port $Port on $ComputerName is actively listening and responsive (${TimeoutMs}ms limit)." -ForegroundColor Green
    } catch {
        throw "Tier 2 Failed: Port $Port on $ComputerName connection failed: $($_.Exception.Message)"
    } finally {
        $client.Close()
        $client.Dispose()
    }
}
```

### 3. Universal Process Lifecycle Invariance Assertion (Tier 3)
```powershell
function Assert-ProcessConfigPersistence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ProcessName,
        [Parameter(Mandatory=$true)][scriptblock]$ConfigCheckScript
    )

    & $ConfigCheckScript
    $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
    if ($proc) {
        $proc | Stop-Process -Force
        Start-Sleep -Seconds 2
    }
    try {
        & $ConfigCheckScript
        Write-Host "  [PASS] Configuration persisted across '$ProcessName' process lifecycle." -ForegroundColor Green
    } catch {
        throw "Tier 3 Failed: Configuration was overwritten or corrupted upon '$ProcessName' restart: $_"
    }
}
```

### 4. Universal Cumulative Regression Test Runner (Tier 4)
```powershell
function Invoke-CumulativeRegressionSuite {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$TestSuitePath)

    if (-not (Test-Path $TestSuitePath)) {
        throw "Regression Suite Missing: Cannot find test suite at '$TestSuitePath'."
    }
    $pesterResult = Invoke-Pester -Path $TestSuitePath -PassThru -Output None
    if ($pesterResult.FailedCount -gt 0) {
        throw "Tier 4 Cumulative Regression FAILED: $($pesterResult.FailedCount) test(s) failed out of $($pesterResult.TotalCount) total assertions."
    }
    Write-Host "  [PASS] Tier 4 Regression Passed: All $($pesterResult.TotalCount)/$($pesterResult.TotalCount) assertions verified intact." -ForegroundColor Green
}
```

### 5. Universal Registry Policy & Behavior Assertion (Tiers 1 & 2)
```powershell
function Assert-RegistryPolicyBehavior {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$RegistryPath,
        [Parameter(Mandatory=$true)][string]$ValueName,
        [Parameter(Mandatory=$true)]$ExpectedValue,
        [scriptblock]$BehavioralCheck = $null
    )

    $prop = (Get-ItemProperty -Path $RegistryPath -Name $ValueName -ErrorAction Stop).$ValueName
    if ($prop -ne $ExpectedValue) {
        throw "Tier 1 Failed: Registry value '$ValueName' at '$RegistryPath' is '$prop', expected '$ExpectedValue'."
    }
    if ($BehavioralCheck) {
        & $BehavioralCheck
    }
    Write-Host "  [PASS] Policy '$ValueName' at '$RegistryPath' verified syntactically and behaviorally." -ForegroundColor Green
}
```

### 6. Universal Scheduled Task Readiness Assertion (Tiers 1 & 2)
```powershell
function Assert-ScheduledTaskReady {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$TaskName,
        [string]$TaskPath = "\"
    )

    $task = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction Stop
    if ($task.State -eq "Disabled") {
        throw "Tier 1 Failed: Scheduled task '$TaskName' is Disabled."
    }
    $info = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath -ErrorAction Stop
    if ($task.State -notin @("Ready", "Running")) {
        throw "Tier 2 Failed: Task '$TaskName' is in unexpected state '$($task.State)'."
    }
    Write-Host "  [PASS] Scheduled Task '$TaskName' is primed and ready." -ForegroundColor Green
}
```

### 7. Universal Bootloader & Storage Isolation Assertion (Tier 3 Safety Invariant)
```powershell
function Assert-BootloaderIsolation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][int]$TargetDiskNumber,
        [switch]$RequireEfiIsolation = $true
    )

    $systemDrive = $env:SystemDrive
    $osPartition = Get-Partition -DriveLetter $systemDrive.TrimEnd(':') -ErrorAction Stop
    if ($TargetDiskNumber -eq $osPartition.DiskNumber) {
        throw "FATAL SAFETY INVARIANT VIOLATION: Target Disk $TargetDiskNumber hosts active OS ($systemDrive)!"
    }

    if ($RequireEfiIsolation) {
        $espPartitions = Get-Partition | Where-Object { $_.GptType -eq "{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}" -or $_.IsSystem -eq $true }
        $activeEspDisks = $espPartitions | ForEach-Object { $_.DiskNumber } | Select-Object -Unique
        if ($activeEspDisks -contains $TargetDiskNumber) {
            throw "FATAL SAFETY INVARIANT VIOLATION: Target Disk $TargetDiskNumber contains active ESP bootloader!"
        }
    }
    Write-Host "  [PASS] Storage Invariant: Disk $TargetDiskNumber is safely isolated from OS and active ESP." -ForegroundColor Green
}
```

### 8. Universal Target Environment Identity Assertion (Management Host Shield)
```powershell
function Assert-TargetEnvironmentIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ExpectedTargetHostname,
        [switch]$AllowAnyHost = $false
    )

    if ($AllowAnyHost) { return }
    $currentHost = $env:COMPUTERNAME
    if ($currentHost -ne $ExpectedTargetHostname) {
        throw "FATAL TARGET MISMATCH: Execution on host '$currentHost', expected '$ExpectedTargetHostname'. Aborted!"
    }
    Write-Host "  [PASS] Target Environment Identity Confirmed: '$currentHost' matches '$ExpectedTargetHostname'." -ForegroundColor Green
}
```

### 9. Universal Protected System Artifact Assertion (Anti-Naive-Query Rule)
```powershell
function Assert-ProtectedSystemArtifact {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [int64]$MinimumSizeBytes = 0,
        [int64]$MaximumSizeBytes = [int64]::MaxValue
    )

    $exists = [System.IO.File]::Exists($Path)
    $length = 0

    if ($exists) {
        $length = (New-Object System.IO.FileInfo($Path)).Length
    } else {
        $parent = [System.IO.Path]::GetDirectoryName($Path)
        $fileName = [System.IO.Path]::GetFileName($Path)
        $item = Get-ChildItem -Path $parent -Filter $fileName -Force -Hidden -System -ErrorAction SilentlyContinue
        if ($item) {
            $exists = $true
            $length = $item.Length
        }
    }

    if (-not $exists) {
        throw "Protected Artifact Missing: System file '$Path' does not exist."
    }
    if ($length -lt $MinimumSizeBytes -or $length -gt $MaximumSizeBytes) {
        throw "Protected Artifact Size Violation: File '$Path' is $length bytes, expected between $MinimumSizeBytes and $MaximumSizeBytes bytes."
    }
    Write-Host "  [PASS] Protected System Artifact: '$Path' exists with valid length $length bytes." -ForegroundColor Green
}
```

### 10. Universal Power Subsystem Authority Assertion (Kernel Authority Rule)
```powershell
function Assert-PowerSettingAuthority {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$SubgroupGuid,
        [Parameter(Mandatory=$true)][string]$SettingGuid,
        [Parameter(Mandatory=$true)][string]$ExpectedACIndex,
        [Parameter(Mandatory=$true)][string]$ExpectedDCIndex
    )

    $out = powercfg.exe /qh SCHEME_CURRENT $SubgroupGuid $SettingGuid 2>&1 | Out-String
    $acMatch = ($out | Select-String "Current AC Power Setting Index:\s+(0x[0-9a-fA-F]+)")
    $dcMatch = ($out | Select-String "Current DC Power Setting Index:\s+(0x[0-9a-fA-F]+)")

    $ac = if ($acMatch) { $acMatch.Matches[0].Groups[1].Value.ToLower() } else { "Unknown" }
    $dc = if ($dcMatch) { $dcMatch.Matches[0].Groups[1].Value.ToLower() } else { "Unknown" }

    if ($ac -ne $ExpectedACIndex.ToLower() -or $dc -ne $ExpectedDCIndex.ToLower()) {
        throw "Power Subsystem Mismatch for Setting '$SettingGuid': AC=$ac (expected $ExpectedACIndex), DC=$dc (expected $ExpectedDCIndex)."
    }
    Write-Host "  [PASS] Power Setting Authority: Setting '$SettingGuid' confirmed at AC=$ac, DC=$dc." -ForegroundColor Green
}
```

### 11. Universal Multi-Witness Incongruity Assertion (Anti-False-Negative Rule)
```powershell
function Assert-MultiWitnessIncongruity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$FeatureName,
        [Parameter(Mandatory=$true)][bool]$IntentWitness,
        [Parameter(Mandatory=$true)][bool]$SubsystemWitness,
        [bool]$ArtifactWitness = $true
    )

    if ($IntentWitness -and $SubsystemWitness -and -not $ArtifactWitness) {
        throw "INCONGRUITY ANOMALY DETECTED in '$FeatureName': Configuration intent and subsystem report feature is ACTIVE, but artifact probe failed. The test query itself is flawed or probing a locked resource!"
    }
    if (-not $IntentWitness -and $SubsystemWitness) {
        throw "INCONGRUITY ANOMALY DETECTED in '$FeatureName': Subsystem is active despite configuration intent being disabled."
    }
    Write-Host "  [PASS] Multi-Witness Coherence Confirmed for '$FeatureName'." -ForegroundColor Green
}
```

### 12. Universal Low-Level Battery Subsystem Assertion (ACPI Power Authority)
```powershell
function Assert-BatteryHealthAuthority {
    [CmdletBinding()]
    param(
        [double]$MinimumHealthPercent = 80.0,
        [string]$ReportPath = "$env:TEMP\bat_audit.xml"
    )

    & powercfg /batteryreport /xml /output $ReportPath | Out-Null
    if (-not (Test-Path $ReportPath)) {
        throw "Failed to generate ACPI battery report via powercfg."
    }

    try {
        [xml]$xml = Get-Content $ReportPath -Raw
        $bat = $xml.BatteryReport.Batteries.Battery | Select-Object -First 1
        if (-not $bat) {
            throw "No ACPI-compliant battery detected in hardware topology."
        }

        $design = [double]$bat.DesignCapacity
        $full = [double]$bat.FullChargeCapacity
        $cycles = $bat.CycleCount

        if ($design -le 0 -or $full -le 0) {
            throw "Invalid battery capacity reported: Design=$design, Full=$full."
        }

        $health = [Math]::Round(($full / $design) * 100, 2)
        if ($health -lt $MinimumHealthPercent) {
            throw "Battery health failed: Observed $health% (Full=$full mWh, Design=$design mWh). Below threshold $MinimumHealthPercent%."
        }

        Write-Host "  [PASS] Battery Health: $health% ($full mWh / $design mWh, Cycles: $cycles)." -ForegroundColor Green
        return [PSCustomObject]@{
            HealthPercent  = $health
            FullCharge_mWh = $full
            Design_mWh     = $design
            CycleCount     = $cycles
            Chemistry      = $bat.Chemistry
            Manufacturer   = $bat.Manufacturer
        }
    } finally {
        Remove-Item $ReportPath -Force -ErrorAction SilentlyContinue
    }
}
```

### 13. Universal Remote Administrative Token Assertion (UAC Elevation Authority)
```powershell
function Assert-RemoteTokenPrivilege {
    [CmdletBinding()]
    param(
        [string[]]$RequiredPrivileges = @("SeDebugPrivilege", "SeTakeOwnershipPrivilege", "SeLoadDriverPrivilege")
    )

    $privs = & whoami /priv
    $missing = @()

    foreach ($p in $RequiredPrivileges) {
        if ($privs -notmatch $p) {
            $missing += $p
        }
    }

    if ($missing.Count -gt 0) {
        throw "Remote session lacks required administrative privileges: $($missing -join ', '). Session is running in a filtered or un-elevated UAC token context!"
    }

    Write-Host "  [PASS] Remote Administrative Token Verified with active elevated privileges." -ForegroundColor Green
}
```

### 14. Universal Remote Diagnostics Transport Harness (`scripts/Invoke-RemoteTargetDiag.ps1`)
The skill bundles `scripts/Invoke-RemoteTargetDiag.ps1`, which guarantees 100% transport fidelity over OpenSSH:
- **AST Pre-Parsing**: Pre-validates PowerShell syntax on the host using `[System.Management.Automation.Language.Parser]` before touching the network.
- **Quote Invariance**: Encodes payloads $\le 6000$ characters as UTF-16LE Base64 for `-EncodedCommand` execution.
- **Large-Script Staging**: Automatically stages payloads $> 6000$ characters via `scp` to `%TEMP%` and executes via `-File`, completely eliminating the Windows 8,191-character command-line limit.

---

## Universal Checkpoint Protocol

Before reporting any milestone or task completion to the user, the agent must output a structured **Verification Manifest**:

```markdown
### Verification Manifest: [Task Name]
- **Target OS / SKU**: Windows 11 Home (Build 26200)
- **Subsystem**: [e.g. Memory Management / SysMain]
- **Tier 1 (Syntactic)**: PASS (Registry Start = 4 confirmed)
- **Tier 2 (Behavioral)**: PASS (Start-Service threw System.InvalidOperationException Error 1058)
- **Tier 3 (Invariant)**: PASS (Verified post-reboot / post-process cycle)
- **Tier 4 (Cumulative Regression)**: PASS (Ran full suite: 46/46 assertions passed, 0 failed)
```
