---
name: software-catalog
description: MUST be read before editing provisioning/catalog.toml or the bake's catalog emitter — any time you add/remove/change a package's present/absent/deactivated state, or mark something for removal from the image. Encodes the dependency-graph rule for Debian/apt: purging a package force-removes its reverse-dependencies, so a "danger" that a kept package hard-depends on must be DEACTIVATED (mask the unit), never purged. Stops the class of bug where purging nfs-common/udisks2 cascaded away the whole RPi desktop.
roles: [infrastructure]
metadata:
  tags: [catalog, software-catalog, apt, deb, dependencies, purge, absent, present, deactivated, mask, provisioning, bake, cloud-init, cascade, reverse-depends, package]
---

# Software catalog — deb dependency rules

`provisioning/catalog.toml` is **declarative data**: each entry is a resource the box must
hold in a `state`. The bake (`bake-image.sh`, `apply_catalog`) turns it into cloud-init
`runcmd`s. Before editing it, know what each state DOES — getting `absent` wrong silently
deletes packages you wanted to keep.

## The three states → what the emitter does

| state | apt manager | systemd manager |
|-------|-------------|-----------------|
| `present` | `apt-get install -y <name>` | (n/a) |
| `absent` | **`apt-get purge -y <name>`** | (n/a) |
| `deactivated` | (keep the package) | `systemctl disable --now <unit>; systemctl mask <unit>` |

## THE RULE (why `absent` is dangerous)

`apt-get purge X` does **not** just remove `X` — it **force-removes every package that
hard-depends on `X`** (a `Depends:`, directly or transitively). So if anything you want to
KEEP depends on the package you mark `absent`, purging it **cascades** and removes the thing
you wanted to keep.

> Real incident (Decision-078): the catalog marked `nfs-common` and `udisks2` `absent`. RPi's
> desktop base `rpd-common` **`Depends:` nfs-common**, and reaches `udisks2` via
> `rpd-common → gvfs → gvfs-daemons → udisks2`. Purging them cascaded and deleted the desktop
> core (`rpd-common`, `rpd-wayland-core`, `rpd-x-core`) → the greeter came up as a bare
> gray screen with a cursor (no `pi-greeter`), and the panel lost its text.

**Hard vs soft:** only `Depends:` (and `Pre-Depends:`) cascade. `Recommends:`/`Suggests:` do
NOT — a package only *Recommended* by something you keep is safe to purge.

**You cannot keep a package and drop its hard dependency.** "Installed `Y` + purged its
`Depends:` `X`" is not a state dpkg/apt will hold (it would be broken/unsatisfied). The only
coherent choices are *keep both* or *remove both*. There is no "remove the dependency, keep
the dependent intact."

## Decision procedure — before you mark anything `absent`

1. **Dry-run the purge and read what else it takes:**
   `apt-get -s purge <pkg>` → look at every `Remv …` line.
2. **If `Remv` lists ONLY your target** (and other things you also want gone) → `absent` is
   safe. Use it.
3. **If `Remv` would remove a package you want to KEEP** (anything the catalog marks
   `present`, the desktop, etc.) → your target is a *hard dependency* of that package. **Do
   NOT purge.** Instead:
   - mark the package itself `present` (or omit it — it stays as a dependency), and
   - kill the actual danger with a `[systemd."<unit>".]` entry, `state = "deactivated"`
     (masks the running service while the package stays for its dependents).
4. **Confirm the dependency direction** when unsure:
   `apt-cache rdepends <pkg>` (who depends on it) and
   `apt-cache show <dependent> | grep -E '^Depends:|^Recommends:'` (hard vs soft).

## Worked example (the fix this skill came from)

```toml
# WRONG — cascades into the desktop:
[apt.udisks2]
state = "absent"          # rpd-common → gvfs → … → udisks2 (hard) → purge kills the desktop

# RIGHT — keep the package, mask the danger:
[apt.udisks2]
state = "present"         # desktop hard-dep; cannot be purged
[systemd."udisks2.service"]
state = "deactivated"     # automount daemon masked → no auto-mounting, desktop intact
```

`avahi-daemon`, `rpcbind`, `wayvnc` stay `absent`: dry-run shows no kept package hard-depends
on them (e.g. `rpcbind` is only `Recommends:`-ed), so their purge does not cascade.

## Backstop (defence in depth, not a substitute)

The bake emitter wraps every purge in a guard: it dry-runs `apt-get -s purge` per package and
**skips** it (emitting `themis-catalog-SKIP-PURGE:<pkg>`) if it would remove a protected
desktop package (`rpd-*`, `lightdm`, `labwc`, `pi-greeter`, `gvfs`, …). This stops a
mis-classified `absent` from shipping the bug again — but the catalog author is still
responsible for classifying correctly (the guard only protects the desktop set, and silently
skipping a purge you *intended* leaves the danger live).

## Always

- **Idempotent + guarded** (AGENTS.md): every generated step must be safe to re-run and act
  only when the target is present/not-already-in-state.
- **Config never in code** (AGENTS.md): the catalog is the management surface; don't hardcode
  package lists in the bake.
- After editing, **test the emitter** without a re-bake: run the embedded generator against
  `catalog.toml` into a temp seed dir and inspect the generated `user-data` (install / mask /
  guarded-purge lines) before trusting it.
