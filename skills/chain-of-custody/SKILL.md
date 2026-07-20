---
name: chain-of-custody
description: Maintain a forensically sound, command-level chain-of-custody record whenever handling an evidence item (drive, disk image, SD/SIM card, phone, laptop volume) or running any command against it. Logs every command with authoritative systemd-journal timestamps, exit codes, and output hashes; registers evidence identity (make/model/serial/UUID/host); records write-protection applied; and appends to EVIDENCE-HANDLING-LOG.md with an honest-limitations note. Invoke BEFORE touching evidence and keep it running for the whole session.
roles: [security/forensics]
---

# Chain of custody

Every action against evidence is a custody event. If it isn't logged, it didn't happen — and it
can taint everything else. Log **commands, S3 operations, mounts, hashes, who, what, when** on the
**clean analysis host only** (`themis`, the Pi). Never run analysis on a machine treated as
compromised.

## 1. Open the record (once per session)
```bash
CASE=neptune                       # case slug
COC=/home/sudoku/rescue/coc/${CASE}-$(date -u +%Y%m%d).coc.md
OPERATOR="S. Lambla"               # who is accountable
HOST="$(hostname) ($(uname -srm))"
{ echo "# Chain of custody — $CASE"; echo "- Operator: $OPERATOR"; echo "- Host: $HOST";
  echo "- Session start (UTC): $(date -u +%FT%TZ)"; echo; echo "## Commands"; } >> "$COC"
```

## 2. Register each evidence item BEFORE reading it
Capture the physical identity so the log ties bytes to an object:
```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,LABEL /dev/sdX
udevadm info --query=all --name=/dev/sdX | grep -Ei "ID_SERIAL|ID_MODEL|ID_VENDOR|ID_FS_UUID"
```
Record: make/model, **serial**, connection (enclosure/chipset), filesystem, volume UUID, role
(source-evidence vs analysis-scratch vs destination).

## 3. Apply + log write-protection (read-only is mandatory for source evidence)
```bash
sudo blockdev --setro /dev/sdX          # kernel read-only; RE-APPLY after any physical re-plug
sudo blockdev --getro /dev/sdX          # confirm = 1
```
Use only read-only tooling for filesystems (`fsapfsinfo`/`fsapfsmount`, `apfs-fuse -o ro`,
`mount -o ro,noload`, `ntfs-3g -o ro`). Note: software read-only is **not** a hardware
write-blocker — state that limitation (§6).

## 3b. ⚠ NEVER log a reader's "empty / missing / dead" as a finding — CHECK `FAILS.md` FIRST
The FUSE readers routinely render volumes **falsely empty**: `libfsapfs` (`fsapfsinfo`/`fsapfsmount`)
can't do snapshots or LZFSE; `apfs-fuse` hits catalog-read bugs on some containers. A negative from
either is **not** a custody finding until cross-checked:
1. read the **APSB `files=`/`dirs=` count** (`apfsutil <dev>`, or the case's apsb dump) — that's the
   ground truth of how many files exist;
2. try `apfs-fuse -o snap=<XID>` and `-o xid=<XID>`;
3. if it still under-reports, **decrypt to a plaintext image → mount with the kernel `apfs` module**.

**Read `FAILS.md` before trusting any tool's absence, and APPEND every new tool trap to it** — that
file is why the next handler doesn't re-make the call. (Proven: "Whitehole" read empty 3× while its
APSB said `files=87`; `M4.jmg` "truncated" was the same false-negative class.) Recording a blind
reader's empty output as fact is a chain-of-custody error — it asserts absence that isn't real.

## 4. Run every command through the custody wrapper
```bash
coc() {  # coc "<why>" <command...>
  local why="$1"; shift
  local t0; t0=$(date -u +%FT%TZ)
  printf '\n- **%s** — `%s`\n  - why: %s\n' "$t0" "$*" "$why" >> "$COC"
  local out; out=$("$@" 2>&1); local rc=$?
  local h; h=$(printf '%s' "$out" | sha256sum | cut -d" " -f1)
  printf '  - exit: %s | output-sha256: %s | end: %s\n' "$rc" "$h" "$(date -u +%FT%TZ)" >> "$COC"
  printf '%s\n' "$out"                      # still show the operator the output
  return $rc
}
# example: coc "inventory LLM" sudo fsapfsinfo /dev/sda2
```
- Timestamps here are host-clock (`date -u`). The **authoritative** times for `sudo` commands are
  in the systemd journal — cross-reference with `journalctl _COMM=sudo --since ...` and mark those
  entries **[J]** in the final log.
- Hashing the output means the record can't be silently edited later.

## 5. Log non-command events too
Mounts, unmounts, drive connect/disconnect (with the dmesg line + serial), S3 uploads (bucket, key,
version-id, ETag — see `write-to-s3`), signatures produced (see `digital-signature`), and any manual physical
handling. One line each, timestamped.

## 6. Close the record — with honest limitations
Before ending, append a limitations section stating exactly what was and wasn't guaranteed, e.g.:
- write-protection was software-based, no hardware write-blocker;
- whether a verified forensic image was made or only logical/read-only access;
- any tool that gave uncertain/failed results.
Then fold the session's key events into `/home/sudoku/rescue/EVIDENCE-HANDLING-LOG.md` (the
owner-facing custody document, formatted per its existing sections and `[J]` convention).

## Rules
- Clean host only; compromised machines stay powered off.
- Read-only on all source evidence; re-apply `--setro` after every re-plug.
- Log first, act second. Never delete an original until its copy is hash-verified AND signed
  (see `digital-signature`) AND, for cloud, Object-Locked (see `write-to-s3`).
- "Not a certified forensic examination" unless a hardware write-blocker + verified image were used —
  say so plainly.
