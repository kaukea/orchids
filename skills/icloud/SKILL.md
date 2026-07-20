---
name: icloud
description: Retrieve a user's OWN iCloud data (photos, Drive) off an already-signed-in Apple device before it is lost, WITHOUT touching account control — for when the account cannot be re-authenticated (burned/lost 2FA) but existing trusted sessions still work. Covers Photos "Download Originals", incremental exfiltration against a remote-wipe race, the signed-in-session-only constraint, and the do-NOT-touch-Apple-ID boundary. Pairs with machine-access, chain-of-custody.
roles: [security/forensics]
---

# iCloud data retrieval (signed-in session only)

When the Apple account cannot be re-authenticated (2FA lost/burned) but a device still holds a **live
signed-in session**, that session can PULL DATA even though it cannot manage the account. This skill
gets the data off before it is lost. Read-only on the source; never touch Apple ID / account control.

## Preconditions
- A device (Mac or phone) with a **live signed-in iCloud session**. You cannot re-auth / add a new device.
- Access to that device's desktop/session — see `machine-access` for getting into a locked Mac.

## Do NOT touch Apple ID (hard boundary)
Account-control surfaces (Find My, appleid/icloud.com, sign-out/in, 2FA changes) re-challenge identity
and can demand the lost factor — and Find My is the remote-**WIPE** lever. Never toggle Find My, never
sign out/in. **Data-pull only.**

## Photos — full-resolution originals
Signed-in Mac: **Photos.app → Settings → iCloud → "Download Originals to this Mac"** (NOT "Optimize Mac
Storage"). Pulls every original into `~/Pictures/Photos Library.photoslibrary/originals/`. The iCloud.com
web download needs a fresh sign-in (verification) — unavailable, skip it.

## Incremental exfiltration (the wipe race)
Any device on a hostile account is remote-wipe-exposed the moment it is online. So **copy the data off
AS IT LANDS** — to an attached external / a network drop — continuously, not in one shot at the end. A
wipe mid-download then costs only the last chunk. This is the only mitigation when Find My is off-limits.

## Storage + throughput
- The library may be large — ensure the target has room, point the library to an external, or
  exfil-and-clear as you go. A too-small disk stalls the pull.
- Keep the device awake, powered, on a solid network. **Parallelize** across multiple signed-in devices
  if available — split the risk and the wall-clock against the deadline.

## Verify + log
Done when the app shows every item local (no cloud badge) and the exfil count/size matches. Log the
retrieval (counts, hashes) via `chain-of-custody`.
