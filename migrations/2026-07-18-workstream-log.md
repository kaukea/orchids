# 2026-07-18 — per-session workstream logs replace HANDOVER.md

The monolithic `HANDOVER.md` becomes a per-stream directory of small rolling
session logs: `.git/the-works/<stream>/<YYYYMMDD-HHMMSS>-<role>.md`, with a
`_closed` marker when a stream awaits ingestion (`handover` skill). Any flat
`HANDOVER*.md` still sitting in `.git/the-works/` (including strays gathered
by the earlier the-works migration) becomes a closed `legacy` stream, so one
ingestion mechanism remains.

## Detect → convert

```sh
gcd="$(git rev-parse --git-common-dir)"
if ls "$gcd/the-works"/HANDOVER*.md >/dev/null 2>&1; then
  mkdir -p "$gcd/the-works/legacy"
  i=0
  for f in "$gcd/the-works"/HANDOVER*.md; do
    [ -f "$f" ] || continue
    i=$((i+1))
    stamp="$(date -r "$f" +%Y%m%d-%H%M%S 2>/dev/null || echo 00000000-000000)"
    mv -n "$f" "$gcd/the-works/legacy/$stamp-legacy-$i.md"
  done
  touch "$gcd/the-works/legacy/_closed"
fi
true
```

## Then: ingest

The `legacy` stream is a normal `_closed` stream: read its files oldest-first,
promote anything durable-looking (decisions, outcomes, deferred work) to its
proper home, archive the directory to `.git/the-works/_ingested/` (`handover`
skill → Ingest).

## Verify

No `HANDOVER*.md` remains directly in `.git/the-works/`; if any existed, they
now sit under `.git/the-works/legacy/` alongside a `_closed` marker (until
ingestion archives the stream to `_ingested/`).
