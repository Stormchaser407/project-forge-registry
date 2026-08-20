# GitHub Estate Archive — Batch Two — 2026-08-19

**Status:** approved disposition; preservation/archive transaction pending  
**Policy:** archive, do not delete  
**Authority:** `docs/GITHUB_ESTATE_LEDGER.md` and `docs/REPOSITORY_LIFECYCLE_STANDARD.md`

Batch Two covers stale vendor/reference forks and one historical OpenClaw workspace snapshot that do not need to remain on the visible active shelf. Unique local commits remain preserved in Git history after archival. None of these repositories is being deleted.

## Batch Two candidates

### 1. `Stormchaser407/OSINT-Framework`

Lifecycle: `reference` → `archived` reference.

Evidence:

- GitHub identifies the repository as a fork of `lockfale/OSINT-Framework`.
- Current comparison: 1 commit ahead, 393 commits behind upstream.
- The unique commit adds `dopamine/colab/agents.ipynb`.
- No current `homelab-nixos-config` dependency was found.

Disposition: preserve the local notebook in the archived fork; use current upstream directly for future vendor code. Any future Cerberus/OSINT harvest can explicitly unarchive or inspect the preserved history.

### 2. `Stormchaser407/cloudfuse`

Lifecycle: `reference` → `archived` reference.

Evidence:

- Fork of `Seagate/cloudfuse`.
- Current comparison: 1 commit ahead, 224 commits behind upstream.
- The unique divergence modifies Docker/build material and removes old Windows-installer material.
- No current `homelab-nixos-config` dependency was found.

Disposition: archive as preserved experiment/vendor delta. Future Cloudfuse use should begin from current upstream unless the archived local delta is deliberately re-evaluated.

### 3. `Stormchaser407/gradle`

Lifecycle: `reference` → `archived` reference.

Evidence:

- Fork of `gradle/gradle`.
- Current comparison: 2 commits ahead, 4,291 commits behind upstream.
- Local divergence is dominated by removals in documentation/sample distribution files rather than a maintained Gradle product fork.

Disposition: archive. Use current Gradle upstream for future dependency/build-tool work.

### 4. `Stormchaser407/agent-zero`

Lifecycle: `reference` → `archived` reference.

Evidence:

- Fork of `agent0ai/agent-zero`.
- Current comparison: 1 commit ahead, 542 commits behind upstream.
- The unique commit preserves an experimental runtime package: systemd service, healthcheck, Podman wrapper, environment example, and runtime README.
- No current `homelab-nixos-config` dependency was found.

Disposition: archive with the runtime experiment preserved in history. Future Agent Zero evaluation should start from current upstream and selectively recover the archived runtime ideas if useful.

### 5. `Stormchaser407/IG-Detective`

Lifecycle: `reference` → `archived` reference.

Evidence:

- Fork of `shredzwho/IG-Detective`.
- Current comparison: 2 commits ahead, 4 commits behind upstream.
- Local divergence contains a real Docker Compose customization.
- No current `homelab-nixos-config` dependency was found.

Disposition: archive as a preserved Cerberus Recon/OSINT reference. The Docker customization remains available for later lawful harvest without presenting this fork as an active current tool owner.

### 6. `Stormchaser407/openclaw-workspace`

Lifecycle: `reference` → `archived` reference.

Evidence:

- Repository contains a single `Initial OpenClaw workspace snapshot` commit from 2026-05-05.
- `IDENTITY.md` identifies that snapshot as `CaseBot 5000`.
- Current OpenClaw runtime/configuration is represented separately in `homelab-nixos-config`, including the active OpenClaw Nix configuration and Space Ghost/Librarian integration.
- No current CaseBot-specific dependency was found in the homelab configuration.

Disposition: archive as historical workspace/reference. This does not archive, disable, or change the live OpenClaw runtime.

## Explicit exclusions from Batch Two

- `Stormchaser407/tidal-hifi` — retain visible: current homelab configuration explicitly includes TIDAL Hi-Fi and multi-scrobbler integration; local fork commits are operationally relevant.
- `Stormchaser407/SpiderFoot_PeopleSearch` — retain: repository documents a live local SpiderFoot runtime and is still an operator-support surface for lawful Cerberus Recon work.
- `Stormchaser407/argus-reference` — retain reference: large sanitized Argus lineage remains relevant to current Argus/Cerberus preservation work.
- `Stormchaser407/MyGirlGPT` and `Stormchaser407/project_katrina` — retain parked/reference pair: Project Katrina explicitly references MyGirlGPT and its local Katrina integration.
- `Stormchaser407/Technical_Documents` — retain `waiting` until N5/Librarian migration can preserve the document corpus outside GitHub.
- `Stormchaser407/CreeperBot5000` — retain `waiting` until the fleet census inspects the known possible local ancestor lineage.
- `Stormchaser407/marioncounty-weather-wise` — retain `waiting` for final external Lovable/deployment-binding disposition. Its Git history and README blob match the preferred organization-owned `endgame-solutions/marion-county-weather-hub`, but an external binding should not be guessed from Git identity alone.

## Gate

Before GitHub archive flags are applied, each Batch Two repository should receive a visible preservation/archive notice naming its upstream or surviving authority and explicitly stating that source/history are retained. After archival, verify all six repositories report `archived=true` and record the resulting estate count.
