---
name: reverse-engineering-files
description: Reverse-engineer an unknown or opaque file / on-disk format so it can be read losslessly, and CAPTURE what you learn as a reusable `formats/<name>.md` doc + a `tools/` parser so no future session re-derives it. Invoke whenever you hit a file whose structure you don't fully understand (unknown extension, custom/renamed image, proprietary DB, binary blob, container, keychain, journal, index) BEFORE trusting any single tool's read of it. Pairs with read-apfs, chain-of-custody.
roles: [development/file-formats, security/forensics]
---

# Reverse-engineering file / on-disk formats

The rule this skill enforces (CLAUDE.md §22): **the moment you understand a format, write it down.**
Every format figured out and not documented is a format the next session pays to re-learn — and this
project has already lost days to exactly that. A format is "done" only when there is a
`formats/<name>.md` **and** a reusable reader in `tools/`, both validated against real data.

## 0. Identify by CONTENT, never by name (rules 5–8)
An extension is a hint, not a fact (`.jmg` here was an ad-hoc rename; `.keychain-db` files are
`kych`, not SQLite). Start from bytes:
```bash
xxd -l 64 <file>            # or: od -A x -t x1z <file> | head
xxd -s <off> -l 4 <file>    # probe a specific structure offset
file <file>; binwalk <file> # generic guesses / embedded-content scan
python3 -c "import sys,math,collections as c; d=open(sys.argv[1],'rb').read(1<<16); \
 h=-sum((n/len(d))*math.log2(n/len(d)) for n in c.Counter(d).values()); print('entropy',round(h,2))" <file>
# entropy ~8.0 = encrypted/compressed; ~4-6 = structured/text; low = sparse/padding
```
Magic-byte leads collected on this project: `NXSB` APFS container (+0x20), `APSB` volume superblock,
`kych` old macOS keychain, `SQLite format 3\0`, `1SLD/2SLD/3SLD` fsevents pages, `bplist00` binary
plist, `encrcdsa` FileVault-dmg v2 token, `koly` UDIF trailer (EOF−512), `eyJ` base64 JWT,
`-----BEGIN` PEM. Add every new one you confirm.

## 1. RESEARCH before guessing
If the magic/structure isn't obvious, search online FIRST (the format usually has a spec or a
reverse-engineer's writeup) — cite it. Check: the vendor's own reference (Apple File System
Reference), `libyal`/`mac_apt`/forensics tooling source, and prior RE blog posts. Note the tool's
**limitations** (e.g. `libfsapfs` can't do snapshots/LZFSE) — those become gotchas in the doc.

## 2. Read structurally, cross-check, VALIDATE against an oracle
- Parse fields at their real byte offsets, little/big-endian as the format dictates (Apple on-disk
  = LE; network/DER = BE). Watch version-dependent record layouts (fsevents 3SLD adds a `node_id`
  that breaks fixed-size parsers — resync instead).
- **Never trust one reader.** Cross-check a second tool or the raw bytes. A reader's "empty/dead"
  is not a finding (see `read-apfs`, `FAILS.md`).
- **Validate**: decode something whose answer you already know (a live file's known content, an APSB
  `files=` count, a hash that must match). If the parser reproduces the oracle, trust it; else it's
  wrong. (E.g. the SaFE VEK decryptor was trusted only after it reproduced `cryptomator`/`APSB`
  plaintext from known blocks.)

## 3. WRITE `formats/<name>.md` — the deliverable (do it the same turn)
One file per format, following the existing ones (`formats/apple-fsevents.md`,
`spotlight-store.md`, `apfs-filevault.md`, `apple-messages.md`, `sparsebundle.md`, …). Include:
- **What it is** + where it's found; **magic bytes** + how to confirm identity by content.
- **On-disk structure**: field offsets/sizes/endianness, record layout, version differences.
- **How to read it** read-only (exact commands/flags), and the **gotchas/traps** that cost you time.
- **Tool**: the parser you built (path) + how to run it. **Sources**: every reference, cited.

## 4. BUILD a reusable reader in `tools/` (repo, never /tmp — rule F.13)
A doc without a tool gets re-implemented; a tool without a doc gets misused. Ship both. Keep the
tool **read-only** on evidence, operating on staged copies. Make its PRIMARY output the reliable
part (e.g. path strings) and label best-effort parts as such. Add a one-line self-test / oracle
check where possible. Cross-link the tool README ↔ the format doc.

## 5. Log it (custody)
Reverse-engineering evidence IS evidence access — run reads through the `chain-of-custody` wrapper,
and if the format work revealed recoverable data, record it in `RECOVERED.md` + `keys/FOUND.txt`
(secrets go to the ledger, with a comment, per the owner).

## Checklist (a format is DONE when all are true)
- [ ] Identified by content/magic, not extension.  - [ ] Researched + cited if non-obvious.
- [ ] Parsed structurally and **validated against an oracle**.  - [ ] `formats/<name>.md` written.
- [ ] Reusable `tools/` reader committed + linked.  - [ ] Custody/RECOVERED/FOUND updated.
