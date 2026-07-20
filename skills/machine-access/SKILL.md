---
name: machine-access
description: Get into a locked / attacker-changed Mac READ-ONLY for a forensic data pull, without lowering security or modifying the machine. Covers the credential paths (FileVault recovery key = LOCAL reset on Intel/T2; PIV smart-card preboot on Apple Silicon; free in-session dscl -authonly credential testing), preboot vs recoveryOS, the SEP finite-attempt trap, and the "extract, don't mess" boundary. Pairs with icloud, disk-imaging, chain-of-custody.
roles: [security/forensics]
---

# Machine access (locked Mac, forensic, read-only)

Reach a locked / attacker-changed Mac's desktop or recoveryOS to pull data — WITHOUT modifying the
machine (no password resets, no persistence changes, no reconfig) and without lowering its security.

## Credential paths
- **FileVault recovery key (Intel / T2):** at the login screen it resets the **LOCAL** password — a
  local operation that does NOT touch Apple ID. The clean way into an Intel Mac whose password was changed.
- **PIV / smart-card (Apple Silicon):** a paired smart-card can unlock FileVault at the **preboot**
  screen for its account, bypassing an unknown local password — but ONLY if the card is actually paired
  and presented at preboot. Verify it; it is not guaranteed (a card that works for post-boot login may
  do nothing at preboot).
- **In-session credential test (FREE):** once on any desktop, test candidate admin passwords with
  `dscl . -authonly <user> '<pw>'` — LOCAL, does NOT spend the SEP/FileVault attempt pool. Confirm a
  password here BEFORE ever typing it at a preboot/recoveryOS screen. Also check
  `sysadminctl -secureTokenStatus <user>` + `fdesetup list` to learn whether that account can unlock in
  recoveryOS (required for imaging).

## The SEP trap — never gamble at the screen
The FileVault/SEP preboot has a FINITE, TERMINAL attempt pool (~10, then the disk locks forever).
**Never type a guessed password there.** Confirm every credential in-session (dscl, free) first, so the
screen entry is a single known-good unlock. If throttled, WAIT — do not reboot (a reboot restarts the timer).

## Preboot vs recoveryOS
- Normal boot → desktop → live logical collection + iCloud pull (`icloud`).
- recoveryOS (hold power) → unlock the Data volume with a confirmed secure-token password, then image it
  (`disk-imaging`). recoveryOS is forensically cleaner — the compromised OS never boots.

## Boundary — extract, don't mess
Read-only on the machine. Do NOT reset passwords, kill persistence, or reconfigure — that is recovery,
not forensic extraction. Never network a compromised machine unless the owner has explicitly accepted the
risk for a specific data pull. Log every access via `chain-of-custody`.
