---
name: forensic-acquisition
description: Full end-to-end forensic acquisition of a storage device for evidence — evidence numbering, photographing the device (with the exhibit number in frame), documenting the media, write-blocking, imaging to E01 with acquisition+verification hashing, integrity disclosure, optional certified secure-erase of repurposed media, and the signed manifest/attestation. Invoke to acquire ANY drive/card/media as a numbered exhibit. Exhibit-01 (SanDisk SD card) is the worked template. Pairs with chain-of-custody, read-apfs, digital-signature, write-to-s3.
roles: [security/forensics]
---

# Forensic acquisition (numbered exhibit, ISO/IEC 27037)

Principles: **auditability, repeatability, reproducibility.** Clean host only (`themis`), read-only on
the source, disclose every limitation honestly. One case folder per exhibit:
`cases/EXHIBIT-NN_<make>_<serial>/`.

## 1. Intake — number it, PHOTOGRAPH it, document it
- Assign **case number** + **exhibit/evidence ID** (e.g. `01`).
- **Photograph the device** *before* connecting: overview, the label/serial close-up, and at least one
  shot **with the exhibit-number tag/label physically in frame next to the device**. Note anything
  unusual. Save to `PHOTOS/`, fill `PHOTOS/photo-log.md` (photo #, what it shows, UTC time), and
  generate `PHOTOS/SHA256SUMS` over the images.
- Record in `NOTES.md`: description (make/model/capacity in **bytes**), **serial from the label** AND
  as reported by the OS (note: USB readers/enclosures often **mask the real serial** — say so),
  sector size, partition layout.

## 2. Write-protect + disclose integrity events
- `sudo blockdev --setro /dev/sdX` **before** anything reads it; confirm `getro` 0→1 on the disk and
  all partitions. **Hardware write-blocker > software — disclose which** (software is a stated weakness).
- Prevent auto-mount first (`gsettings ... automount false`, or attach with the desktop closed). If an
  **automount race** happens anyway (GNOME/udisks mounting a partition RW on insert), **DISCLOSE it**:
  which partition, that it was RW, and the impact (e.g. "FAT metadata on the boot partition only").
- **Prove the substantive partition was never mounted:** it must be absent from `/proc/mounts`, and a
  no-mount `dumpe2fs -h` (ext) / equivalent shows an **unchanged last-mount time + mount count** (a
  mount would bump both). Record those values.

## 3. Image → E01 (bit-stream, hashed at acquisition)
```
ewfacquire -t cases/EXHIBIT-NN.../EXHIBIT-NN -f encase6 -c deflate:best -S 2GiB \
           -b 64 -d sha256 /dev/sdX      # MD5 is computed too; -d sha256 adds SHA-256
```
Record in `NOTES.md`: tool+version (`ewfacquire`/libewf), format (EnCase6/E01, deflate:best, 2 GiB
segments, sectors/chunk, sector size, media physical/removable), **start/end times**, and the
**source-media MD5 + SHA-256 embedded in the E01** (computed during read). Long images: run under a
watchdog → `watchdog.log`. Save `acquire.log` (the hashes) + `acquire.stdout`.

## 4. Verify (this is the reproducible-integrity proof)
```
ewfverify -d sha256 cases/EXHIBIT-NN.../EXHIBIT-NN.E01   # → verify.log
```
Must print **`ewfverify: SUCCESS`** with **stored hash == recomputed hash** over the full media.
Record PASS/FAIL + the recomputed hashes in `NOTES.md`. A negative here = do not proceed.

## 5. Certified secure-erase — ONLY for media being repurposed, NEVER for evidence you keep
- **If the source is EVIDENCE going to the police → do NOT erase. Preserve the physical device**
  (sealed, write-blocked, in the custody chain). Skip this step.
- **Only if the media is your own, being reused** (e.g. Exhibit-01 was the Pi's own card), and **only
  after verify PASS:** zero-fill and prove it:
```
sudo dd if=/dev/zero of=/dev/sdX bs=4M status=progress   # → zerofill.log (method + start/end)
# then verify all-zero (sample/full read-back) and record it — that read-back IS the "erasure cert"
```
Log method, time, and the zero-verification in `NOTES.md` + `zerofill.log`.

## 6. Manifest → attestation → sign
- `MANIFEST.sha256` = SHA-256 of the whole deliverable set (E01 segments, logs, NOTES, PHOTOS/*).
- Build the **attestation** (embeds source-media hashes + the manifest + the disclosed limitations).
  Sign it with **digital-signature** (see the `digital-signature` skill). **Match the level to the destination:**
  - **Going to police / court = a legal matter → QUALIFIED electronic signature + the legal *mention***
    (in **French**, citing **loi n° 1.383 du 2 août 2011 sur l'Économie Numérique, modifiée** +
    **article 1163-3 du Code civil**). Evidence exhibits fall here — use this.
  - **Purely administrative paperwork** (no judge — a request, a form) → simple proof-of-ID signature
    (name + date via PAdES), **no mention** needed.

## Deliverable set (hand over as a unit)
E01 segments + `SHA256SUMS` + `acquire.log` + `verify.log` + `NOTES.md` + `PHOTOS/` (images + `photo-log.md`
+ `SHA256SUMS`) + the signed attestation + `MANIFEST.sha256(.p7s/PDF)`. Examiner work product (scripts,
methodology) is hashed **separately**, never as a numbered exhibit. Offload/preserve via `write-to-s3`.

## Rules
- Read-only + write-block on the source; disclose software-vs-hardware honestly.
- Never treat a reader's "empty" as fact — cross-check (see `read-apfs`, `FAILS.md`).
- Every step is a custody event → log it (see `chain-of-custody`).
- Erase only repurposed media, after verify PASS, with a documented zero read-back. Evidence sources are preserved, not wiped.
- "Not a certified forensic examination" unless a hardware write-blocker + verified image were used — state it.
