# GitHub Estate Archive — Batch Two — 2026-08-19

**Status:** complete — 6/6 repositories archived and verified  
**Completed:** 2026-08-19 (America/New_York)  
**Policy:** archive, do not delete  
**Authority:** `docs/GITHUB_ESTATE_LEDGER.md` and `docs/REPOSITORY_LIFECYCLE_STANDARD.md`

Batch Two covers stale vendor/reference forks and one historical OpenClaw workspace snapshot that no longer need to remain on the visible active shelf. Unique local commits remain preserved in Git history after archival. None of these repositories was deleted.

## Verified result

The authenticated GitHub CLI transaction on Recon completed after a preservation-notice verification correction. The first verification attempt correctly aborted before applying any archive flags because a `pipefail`/`grep -q` broken-pipe condition produced false negatives on large README files. Direct file inspection confirmed the notices had landed. A corrected verifier materialized each README before testing it, and all six notices passed.

Final GitHub state:

1. `Stormchaser407/OSINT-Framework` — `archived=true`
2. `Stormchaser407/cloudfuse` — `archived=true`
3. `Stormchaser407/gradle` — `archived=true`
4. `Stormchaser407/agent-zero` — `archived=true`
5. `Stormchaser407/IG-Detective` — `archived=true`
6. `Stormchaser407/openclaw-workspace` — `archived=true`

Estate state after Batch Two: **51 archived / 36 visible** across the 87-repository reviewed estate.

## Preserved evidence and disposition

### `Stormchaser407/OSINT-Framework`

Final lifecycle: `archived` reference.

- Fork of `lockfale/OSINT-Framework`.
- At review: 1 commit ahead, 393 commits behind upstream.
- Unique commit adds `dopamine/colab/agents.ipynb`.
- No current `homelab-nixos-config` dependency was found.

Future use should begin from current upstream; the archived fork preserves the local notebook for deliberate harvest.

### `Stormchaser407/cloudfuse`

Final lifecycle: `archived` reference.

- Fork of `Seagate/cloudfuse`.
- At review: 1 commit ahead, 224 commits behind upstream.
- Unique divergence modifies Docker/build material and removes older Windows-installer material.
- No current `homelab-nixos-config` dependency was found.

Future use should begin from current upstream unless the preserved local delta is explicitly re-evaluated.

### `Stormchaser407/gradle`

Final lifecycle: `archived` reference.

- Fork of `gradle/gradle`.
- At review: 2 commits ahead, 4,291 commits behind upstream.
- Local divergence was dominated by documentation/sample distribution-file removals rather than a maintained product fork.

Use current Gradle upstream for future build-tool work.

### `Stormchaser407/agent-zero`

Final lifecycle: `archived` reference.

- Fork of `agent0ai/agent-zero`.
- At review: 1 commit ahead, 542 commits behind upstream.
- Unique commit preserves an experimental runtime package containing systemd, Podman, healthcheck, environment-example, and runtime documentation material.
- No current `homelab-nixos-config` dependency was found.

Future evaluation should start from current upstream and selectively recover archived runtime ideas only if useful.

### `Stormchaser407/IG-Detective`

Final lifecycle: `archived` reference.

- Fork of `shredzwho/IG-Detective`.
- At review: 2 commits ahead, 4 commits behind upstream.
- Local divergence contains a real Docker Compose customization.
- No current `homelab-nixos-config` dependency was found.

The archived fork remains a lawful Cerberus Recon/OSINT harvest source without presenting itself as an active tool owner.

### `Stormchaser407/openclaw-workspace`

Final lifecycle: `archived` reference.

- Single `Initial OpenClaw workspace snapshot` commit from 2026-05-05.
- `IDENTITY.md` identifies the snapshot as `CaseBot 5000`.
- Current OpenClaw runtime/configuration lives separately in active `homelab-nixos-config` surfaces.
- No current CaseBot-specific dependency was found.

Archival of this historical workspace does not archive, disable, or alter the live OpenClaw runtime.

## Explicit survivors confirmed during Batch Two review

- `Stormchaser407/tidal-hifi` — retain visible: current homelab configuration explicitly includes TIDAL Hi-Fi and multi-scrobbler integration; local fork commits are operationally relevant.
- `Stormchaser407/SpiderFoot_PeopleSearch` — retain: repository documents a live local SpiderFoot runtime and remains an operator-support surface for lawful Cerberus Recon work.
- `Stormchaser407/argus-reference` — retain reference: large sanitized Argus lineage remains relevant to current Argus/Cerberus preservation work.
- `Stormchaser407/MyGirlGPT` and `Stormchaser407/project_katrina` — retain parked/reference pair: Project Katrina explicitly references MyGirlGPT and its local Katrina integration.
- `Stormchaser407/Technical_Documents` — retain `waiting` until N5/Librarian migration can preserve the document corpus outside GitHub.
- `Stormchaser407/CreeperBot5000` — retain `waiting` until the fleet census inspects the known possible local ancestor lineage.
- `Stormchaser407/marioncounty-weather-wise` — retain `waiting` for final external Lovable/deployment-binding disposition. Its Git history and README blob match the preferred organization-owned `endgame-solutions/marion-county-weather-hub`, but an external binding should not be guessed from Git identity alone.

## Reversibility

All six repositories remain recoverable through GitHub unarchive. Any future unarchive should be deliberate, recorded in Project Forge, and tied to a real implementation or harvest mission.