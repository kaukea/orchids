---
name: orchard
description: Use whenever the operator asks to hide, show, un-hide, or list which repos appear in the fleet sidebar, or invokes `/orchard`. Covers the numbered-list conversational hide/show UX and the direct `/orchard hide <name>` / `/orchard show` forms. Does NOT cover getting a repo INTO the sidebar in the first place — that is automatic (installing orchids in a repo is registration, no add command exists or should be built).
roles: [general]
metadata:
  tags: [orchard, sidebar, hide, show, registry, fleet, repos, orchids-install]
  share: github
---

# Intent (orchard)

The fleet sidebar shows every repo with orchids installed automatically —
`.ai.toml` presence IS the install signal, and installing IS registration
(`tools/orchard_registry.py`, `docs/TODO.md.d/sidebar-polish.md` item 7).
There is **no `/orchard add <path>`** — an earlier version of this was
reverted by the operator and must not be rebuilt. This skill covers only the
other half: letting the operator **hide** a repo they don't want cluttering
the sidebar, and **show** (un-hide) one again — persisted across remounts.

## Checklist

- [ ] Never build or suggest an `add`/`register` command — appearance is automatic
- [ ] Hide/show always resolves to a specific registered repo PATH before writing
- [ ] An ambiguous or missing name falls back to the numbered-list prompt — never guess
- [ ] The pick is persisted via `tools/orchard_registry.py`, not held in conversation memory
- [ ] Confirm back to the operator which repo was hidden/shown, by its displayed name

## Forms

**`show` (list hidden repos)** — operator says "show hidden repos" / `/orchard show`:

```sh
python3 "$(git rev-parse --show-toplevel)/tools/orchard_registry.py" list
```

Filter to the `[hidden]`-tagged lines, present them as a fresh numbered list (numbers are
this-prompt-only, not stable ids), and ask which to un-hide. Also accept `/orchard show
<displayed-name>` as a direct form — resolve the name against that same hidden set
first.

**`hide <displayed-name>` (direct form)** — resolve `<displayed-name>` against the
`list` output's un-hidden repos. If it matches exactly one, hide it directly:

```sh
python3 "$(git rev-parse --show-toplevel)/tools/orchard_registry.py" hide <path-or-name>
```

**Conversational hide (no argument, or the name given doesn't match exactly one
registered, visible repo)** — this is the primary path, not a fallback edge case:
run `list`, present the currently VISIBLE (non-`[hidden]`) repos as a numbered list of
their displayed names, ask the operator which to hide, then call `hide` with the path
from the picked number. Never hide on a guess — an unclear name always gets the
numbered prompt.

## Rules

- **Hiding is by repo path, never by number alone.** The numbered list is a per-prompt
  UI convenience; resolve the operator's pick back to the path from that same `list`
  output before calling `hide`/`show`, so a stale number from an earlier turn can never
  hide the wrong repo.
- **`orchard_registry.repo_named()` is the resolver** — exact path match first, then
  exact displayed-name (`Path(p).name`) match; ambiguous or no match returns `None`,
  which means: ask, don't guess.
- **Persistence, not memory.** The hide/show pick is written to
  `~/.config/orchids/sidebar-registry.json` by `orchard_registry.py`; it must survive a
  sidebar remount and a new conversation — never track "hidden" only in this turn's
  context.
- **The registry self-heals.** A repo whose `.ai.toml` disappears (uninstalled/deleted)
  drops out of both the registered and hidden lists on the next read automatically — no
  separate uninstall/unhide step is needed for that case.

## Worked example

Operator: "hide the seb.house repo from the sidebar."

```sh
$ python3 tools/orchard_registry.py list
1. orchids  (/home/user/src/serialseb/orchids)
2. seb.house  (/home/user/src/serialseb/seb.house)
3. kauk  (/home/user/src/serialseb/kauk)
```

Name resolves to exactly one entry (`seb.house`) — hide it directly, no numbered
question needed since the name was unambiguous:

```sh
$ python3 tools/orchard_registry.py hide seb.house
seb.house: hidden
```

Reply: "Hidden `seb.house` — it'll stay off the sidebar across remounts. Say `/orchard
show` to bring it back."

If instead the operator just said "hide a repo" with no name, skip straight to: "Which
one? 1) orchids  2) seb.house  3) kauk" and wait for their pick before calling `hide`.
