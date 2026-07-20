---
name: read-apfs
description: Read an encrypted APFS / FileVault2 volume or disk image READ-ONLY for forensic analysis on Linux (no macOS). Covers container/volume/snapshot enumeration, the FileVault keybag chain (recovery key or passphrase → KEK → VEK), mounting with apfs-fuse, and — critically — the recurring FUSE-reader FALSE-EMPTY trap. Invoke whenever mounting or reading any APFS / FileVault drive or image. Pair with the chain-of-custody skill.
roles: [security/forensics]
---

# Read APFS / FileVault (read-only, forensic)

Tools live in `tools/apfs-fuse/build/` (`apfs-fuse`, `apfsutil`, `apfs-dump`, `apfs-dump-quick`) and
the kernel driver source in `tools/linux-apfs-rw`. Full format notes: `formats/apfs-filevault.md`.

## ⚠ GOLDEN RULE — read `FAILS.md` first; never trust "empty / missing / dead"
Both FUSE readers render volumes **falsely empty**: `libfsapfs` (`fsapfsinfo`/`fsapfsmount`) can't do
snapshots or LZFSE; `apfs-fuse` hits **catalog-read bugs** on some containers. A tool's absence is
**NOT a finding** until cross-checked. Proven on this project: "Whitehole" read empty **3×** while its
APSB said `files=87`; `M4.jmg` "truncated/dead" was the same class. **Ground truth = APSB metadata,
not `ls`/`du`.** Log any new trap to `FAILS.md`.

## 1. Identify + write-protect (custody)
```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE /dev/sdX
sudo blockdev --setro /dev/sdX && sudo blockdev --setro /dev/sdX2   # RE-APPLY after any re-plug
```
APFS is partition 2 usually (`sdX2`); `sdX1` is the 200 MB EFI (vfat). For an image, point tools at
the file; use `-s <byte-offset>` if the container sits inside a whole-disk image (GPT first).

## 2. Enumerate — this is the ground truth, do it BEFORE mounting
```bash
tools/apfs-fuse/build/apfsutil /dev/sdX2      # volumes, roles, FileVault y/n, Capacity Consumed, SNAPSHOTS
```
Read the **APSB counts** (`files=`, `dirs=`, `snaps=`) — from `apfsutil` or a case's apsb dump. That
number is how many files MUST appear once mounted. If the mount shows fewer, the reader is blind — not
the data missing. Note which **volume index** apfsutil reports (apfs-fuse `-v` uses it; a container
can have the data volume at index 1 with index 0 empty).

## 3. FileVault unlock — recovery key vs passphrase
Chain: **passphrase or Personal Recovery Key → unwrap KEK → unwrap VEK → decrypt volume.**
- An intruder-**rotated passphrase** does NOT strip the recovery-key KEK — the **recovery key still
  unwraps the VEK** (this is how "Whitehole" opened after the owner's pw failed).
- Pass the key with `-r`: `apfs-fuse -r '<recovery-key-or-passphrase>' …` (it prompts if omitted).

## 4. Mount read-only + VERIFY against the APSB count
```bash
sudo apfs-fuse -o ro,allow_other -v <vol#> -r '<key>' /dev/sdX2 /mnt/x
find /mnt/x -type f | wc -l           # MUST reconcile with APSB files= ; if far fewer → reader blind
```

## 4b. ⚠ A matching file count is necessary but NOT sufficient — sweep the METADATA STORES
Reconciling with APSB `files=` proves the LIVE tree is fully read. It says nothing about files
that were **deleted**. Every APFS/macOS volume carries metadata stores that record — and sometimes
still hold the content of — files gone from the live listing. **Sweep these before calling a volume
"clear/empty/done"** (this is exactly how "SaFE fully cleared" was overturned 2026-07-07: 170 files
incl. a `.fseventsd`/`.Spotlight` layer that named a deleted `Certificates.keychain` +
`pki-sites.key.enc.pem` and let us recover the key's bytes from the Spotlight cache):
```bash
find <mnt> -name .fseventsd -o -name .Spotlight-V100 -o -name .DS_Store -o -path '*/.Trashes/*'
getfattr -R -d -m - <mnt> | grep -i com.apple      # decmpfs (0-byte file, data in xattr!), wherefroms, provenance
```
- `.fseventsd/` → the change **journal**: names deleted paths (`.Trashes/<uid>/…`). Parse with
  `tools/apfs-metadata/parse_fsevents.py`. See `formats/apple-fsevents.md`.
- `.Spotlight-V100/Store-V2/*/Cache/**/*.txt` → cached **content** of indexed (incl. deleted)
  files — grep for `BEGIN .*PRIVATE KEY`, `BEGIN CERTIFICATE`, JWT `eyJ`, text. See
  `formats/spotlight-store.md`.
- `.DS_Store` → Finder's record of folder items (`formats/ds_store.md`). `.Trashes/<uid>/` →
  not-yet-purged deletions. `com.apple.decmpfs` xattr → a file that reads 0 bytes but stores its
  data compressed in the xattr/resource-fork (don't record it as "empty").
Order of recovery once a deletion is found: `.fseventsd` (what) → Spotlight `Cache` (content) →
snapshots/checkpoints (§5, the object) → decrypt-to-image + carve (last resort).
Full tooling: `tools/apfs-metadata/README.md`.

## 5. If it under-reports (fewer files than APSB, or "empty")
In order:
```bash
apfs-fuse -o ro,snap=<XID> -r '<key>' /dev/sdX2 /mnt/x      # snapshot-only data (get XIDs from apfsutil)
apfs-fuse -o ro,xid=<XID>  -r '<key>' /dev/sdX2 /mnt/x      # older checkpoint
apfs-fuse -o ro,allow_other -l -r '<key>' …                # tolerate partial/corrupt catalog
```
Still short (catalog-read bug — e.g. "Whitehole"): **decrypt to a plaintext image, then mount with the
kernel `apfs` module** (reliable catalog, but it can't do FileVault itself — so decrypt first):
- wrapped KEK+IV are in the container keybag (captured in case `apfs-dump-quick.txt`); unwrap with the
  recovery key → VEK → decrypt the container blocks to a plaintext image → `mount -t apfs -o ro <img>`.
- `fsapfsmount` is only ever a quick second opinion, **never the source of a negative.**

## 6. Disk-IMAGE integrity — is the capture COMPLETE, or truncated? (before trusting any image)
A mounted image reading "empty/sparse" can mean a blind reader OR a genuinely incomplete capture —
distinguish by CONTENT, not by a tool's open() success:
- **Segmented UDIF/DMG (`.dmg`+`.NNN` parts):** the `blkx` block table maps every logical sector to
  a compressed chunk (real data OR a zero-fill/ignore chunk for free space). **Complete = chunks
  cover `[0, logical_size)` contiguously, NO GAPS.** Parse the cached blkx and check coverage +
  bytes-by-type (`tools/neptune-reader/verify_coverage.py`). A capture that looks "under-populated"
  is usually just a mostly-empty source disk (free space = zero-fill), NOT missing data — proven on
  Neptune (8.00 TB logical, 3.22 TB real + 4.78 TB zero-fill, 0 gaps = COMPLETE).
- **Raw container image (`.jmg`/`.img`/`.dd`):** read `NXSB` at +0x20, parse `nx_block_size`(+0x24) ×
  `nx_block_count`(+0x28) = **declared container size**; compare to the file size. **declared > file
  = TRUNCATED.** Then check the **FileVault keybag reachability**: `nx_keylocker` paddr (offset
  +0x510 in the superblock) × block_size — if it's **beyond the file**, the keys were never captured
  → **undecryptable, exhaustively** (scan ALL checkpoint superblocks in the captured head for ANY
  keylocker < filesize; if none, it's dead). Proven on `M4.jmg`: 2.00 TB declared, 749 GB captured,
  keybag at 1.80 TB in the missing tail, all 141 superblocks agree → DEAD.

## 7. Time Machine sparsebundle — enumerate EVERY backup, not just the latest
A TM backup disk is an encrypted APFS **sparsebundle**; each backup is an **APFS snapshot** on it.
Mounting one snapshot (e.g. the newest) is NOT the whole history. Chain (per this project):
`device → decrypt/mount the volume holding the bundle → decrypting reader over the bundle bands
(`tools/tm-reader/tmfuse.py`) → losetup -r the decrypted disk.img → apfsutil → apfs-fuse -o snap=<XID>`.
- `apfsutil <decrypted-tm-disk>` lists **all** snapshot XIDs + dates (cross-check
  `com.apple.TimeMachine.SnapshotHistory.plist` in the bundle). Mount any with
  `apfs-fuse -o ro,snap=<XID>`.
- **The reader is single-threaded — it DEADLOCKS on full-tree walks or concurrent snapshot mounts.**
  Do ONE snapshot at a time; for diffs, scope to high-value dirs (not the whole home); small reads.
- For "what changed across time," sample a few snapshots + **diff each against the latest baseline**
  (deleted/changed files surface), rather than walking all of them.

## 8. Access/activity log forensics — see `LOG-FORENSICS.md`
After the filesystem pass, the intrusion evidence (remote access, infection, logins) is in the
**macOS unified logs** (`/var/db/diagnostics` + `uuidtext`). Full taxonomy, the parser build
(`mandiant/macos-UnifiedLogs`), the ~2-day-retention trap, the `<private>`-redaction pivots to
on-disk DBs, and the "which backup's ~2-day window" planning are all in **`LOG-FORENSICS.md`**.
**Checkpoint-scope caveat applies: a backup's logs only testify to ~2 days around that checkpoint —
"clean" ≠ "never compromised."**

## Rules
- Read-only always (`blockdev --setro` + `-o ro`); software RO is not a HW write-blocker — log it.
- Reconcile every mount against the APSB `files=` count. A blind reader's "empty" is a custody error
  if recorded as fact (see the chain-of-custody skill §3b and `FAILS.md`).
- Log the access (device/serial, key used, tool, file count vs APSB) to the custody record.
