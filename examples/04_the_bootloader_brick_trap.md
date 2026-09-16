# The High-Stakes IT Trap: Bootloader Brick

## Scenario
This example highlights one of the most dangerous failure modes of an ungoverned LLM: hallucinating a logical-sounding solution that is technically destructive, simply because the model lacks empirical grounding and wants to be "helpful."

During a hard drive upgrade (migrating from an internal eMMC drive to an NVMe drive via a cloned image), the system's Windows Boot Manager was still pointing to the old eMMC drive's hardware ID. 

**User Request:**
> "I cloned the disk, but the boot is still pointing to the eMMC IDs. How do I fix this?"

---

## ❌ Ungoverned Agent (The "Helpful" Saboteur)
**Result:** The model generates a plausible-sounding but destructive solution based purely on probabilistic text completion, without verifying the underlying hardware state.

**Agent Output:**
> "The system is confused because it sees two identical Windows installations. To force the BIOS to boot from the new NVMe drive, you need to wipe the old eMMC drive. 
> 
> Run `diskpart`, select the eMMC drive, and use the `clean` command."

*What happened?* The user followed the advice. Because the active FAT32 EFI System Partition (which contains the Windows Boot Manager) was still physically located on the eMMC drive, wiping it instantly bricked the bootloader. The laptop became completely unbootable, forcing the user to create a Windows 11 USB installation media to perform a bare-metal repair of the BCD.

---

## ✅ Zero-Trust Agent (With `AGENTS.md`)
**Result:** The agent refuses to provide a destructive command based on an unverified premise. It forces an empirical read-back of the partition table.

**Agent Output:**
[HYPOTHESIS]
Wiping the eMMC drive will resolve the boot conflict and force the system to boot from the NVMe drive.
Current State: UNVERIFIED

[IDENTIFY REQUIRED EVIDENCE]
Before formatting any drive, we must definitively locate the active EFI System Partition (ESP) and verify the current Boot Configuration Data (BCD) paths.

[GROUND VERIFICATION METHOD]
Inspect the active boot manager and partition layout using native Windows utilities (`bcdedit` and PowerShell `Get-Partition`).

[OBTAIN RAW EVIDENCE]
I require the operator to run read-only diagnostic commands to establish the boot layout.

[EXECUTE]
```powershell
bcdedit /enum firmware
Get-Partition | Where-Object { $_.Type -eq "System" }
```

[HARD YIELD TO OPERATOR]

*When the operator returns the command output, the Zero-Trust agent reads the evidence, sees that the EFI partition is on the eMMC, and triggers an `[INCONGRUITY ANOMALY]`, explicitly forbidding the disk wipe.*
