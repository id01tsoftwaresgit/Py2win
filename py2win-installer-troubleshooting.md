# Py2Win — Installer Return Codes & Troubleshooting

**Product:** Py2Win  
**Version:** 1.5.1.0  
**Publisher:** iD01t Productions  
**Support:** admin@id01t.store

This guide documents **what each installer return code means**, how to **diagnose**, and how to **fix** it. Use these commands in an elevated PowerShell terminal to capture logs and exit codes:

```powershell
Start-Process -Wait .\Py2Win-1.5.1.0-Setup.exe '/L=$env:TEMP\py2win_install.log'
$LASTEXITCODE
Get-Content $env:TEMP\py2win_install.log -Tail 200
```

---

## Quick reference (codes mapped for Microsoft Partner Center)

| Scenario | Code |
|---|---:|
| Installation successful | **0** |
| Installation cancelled by user | **1223** |
| Application already exists | **1638** |
| Installation already in progress | **1618** |
| Disk space is full | **112** |
| Reboot required | **3010** |
| Network failure *(mapped)* | **12007** |
| Package rejected during installation *(mapped)* | **1625** |
| Miscellaneous install failure | **1603** |

> **Mapped** = code reserved for the Store’s scenario mapping. Your environment may surface the failure (e.g., policy/AV) before the installer runs.

---

## Supported installer switches

- **Silent install:** `/S`
- **Custom install dir:** `/D="C:\Program Files\Py2Win"`  *(must be last)*
- **Per-user install:** `/ALLUSERS=0`  *(installs to `%LOCALAPPDATA%\Py2Win`)*
- **Desktop shortcut:** `/DESKTOPSHORTCUT=1`
- **Allow overwrite:** `/ALLOWREINSTALL=1`

**Examples**
```powershell
# Default (all users)
.\Py2Win-1.5.1.0-Setup.exe

# Per-user + desktop shortcut
.\Py2Win-1.5.1.0-Setup.exe /ALLUSERS=0 /DESKTOPSHORTCUT=1

# Silent + overwrite if already installed + custom dir (remember /D is last)
.\Py2Win-1.5.1.0-Setup.exe /S /ALLOWREINSTALL=1 /ALLUSERS=0 /D="%LOCALAPPDATA%\Py2Win"
```

---

## Scenario details

### 1) Installation successful — **0**
**Meaning:** Install completed without errors.  
**Verify:** `C:\Program Files\Py2Win\Py2Win.exe` (all users) or `%LOCALAPPDATA%\Py2Win\Py2Win.exe` (per-user).  
**Uninstall (silent):**
```powershell
"C:\Program Files\Py2Win\Uninstall.exe" /S
```

---

### 2) Installation cancelled by user — **1223**
**Meaning:** The user closed the wizard or clicked **Cancel**.  
**Typical log lines:**
- `User aborted installation`  
**Fix:** Re-run the installer and complete all steps.  
**Admin note:** If cancellation happens during a script or RMM push, remove `/S` to show UI and capture screenshots, or re-run with `/S` only after validating prerequisites.

---

### 3) Application already exists — **1638**
**Meaning:** An existing installation was detected in the target scope.  
**Typical log lines:**
- `Existing install detected at: <path>`  
**Fix options:**
- Interactive: confirm **reinstall/overwrite** when prompted.
- Silent: add `/ALLOWREINSTALL=1` or uninstall first.
```powershell
# All users (default scope)
"C:\Program Files\Py2Win\Uninstall.exe" /S

# Per-user (if installed with /ALLUSERS=0)
"%LOCALAPPDATA%\Py2Win\Uninstall.exe" /S
```
**Admin note:** For scripted redeployments, use `/ALLOWREINSTALL=1` to avoid 1638.

---

### 4) Installation already in progress — **1618**
**Meaning:** Another installation process is running.  
**Symptoms:** UI may show a message or the installer exits immediately with 1618.  
**Fix:**
- Wait for the other installer to complete.
- Reboot and run again.
- Ensure RMM/installer scripts are not launching multiple instances.
**Admin note:** Check `msiexec.exe` and other setup processes in Task Manager. Avoid parallel installs in automation.

---

### 5) Disk space is full — **112**
**Meaning:** The destination volume does not have enough free space.  
**Typical log lines:**
- `File: "..\bin\Py2Win.exe"  -> ERROR`  
**Fix:**
- Free up space on the target drive.
- Choose a different **Install Location** or use `/D="D:\Apps\Py2Win"`.
**Admin note:** Ensure at least **200 MB** free for install + temp extraction.

---

### 6) Reboot required — **3010**
**Meaning:** The installation completed but a restart is required to finalize all changes.  
**Fix:** Reboot the device.  
**Admin note:** In automation, treat **3010** as **success with reboot** (do not retry install).

---

### 7) Network failure — **12007** *(mapped)*
**Meaning:** A network stack or name resolution failure was encountered during prerequisite checks or system policies.  
**Fix:**
- Verify the device’s network is online and can resolve domain names.
- Retry after connectivity is restored.
**Admin note:** If using remote shares or network-based prerequisites, map stable paths and ensure firewall/DNS allow access.

---

### 8) Package rejected during installation — **1625** *(mapped)*
**Meaning:** Installation was blocked by device policy (e.g., AppLocker/SmartScreen/Group Policy).  
**Fix:**
- Run as administrator.
- If blocked by policy, request an exception for this package from IT or temporarily allow the publisher.
- Right-click the file → **Properties → Unblock**, then re-run.
**Admin note:** Review Windows Event Viewer → **AppLocker/MSI and Script** logs or **Windows Security → Protection history**. Allow the file hash or path as per policy.

---

### 9) Miscellaneous install failure — **1603**
**Meaning:** Generic failure. Investigate the log for the precise cause.  
**Checklist:**
- Run with logging and review:  
  ```powershell
  Start-Process -Wait .\Py2Win-1.5.1.0-Setup.exe '/L=$env:TEMP\py2win_install.log'
  Get-Content $env:TEMP\py2win_install.log -Tail 200
  ```
- Confirm admin rights (right-click → **Run as administrator**).
- Temporarily disable antivirus or add an exclusion for the installer and `%TEMP%`.
- Ensure the executable in `bin\Py2Win.exe` is present and not quarantined by AV.
- Re-run with UI (without `/S`) to surface any prompts.
**Admin note:** If you see SmartScreen, click **More info → Run anyway** (for unsigned builds).

---

## Uninstall commands

**All users (default scope):**
```powershell
"C:\Program Files\Py2Win\Uninstall.exe" /S
```

**Per-user install (installed with `/ALLUSERS=0`):**
```powershell
"%LOCALAPPDATA%\Py2Win\Uninstall.exe" /S
```

---

## Contact

If you’re still blocked after following these steps, email **admin@id01t.store** with:
- The **return code**
- The last 200 lines of the log file (`%TEMP%\py2win_install.log`)
- Windows version (e.g., Windows 11 23H2) and whether you’re installing **all users** or **per-user**

