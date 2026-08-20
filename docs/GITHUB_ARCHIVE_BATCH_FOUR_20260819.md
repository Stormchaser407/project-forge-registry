# GitHub Estate Archive — Batch Four — 2026-08-19

**Status:** approved disposition; preservation notices written; GitHub archive flags pending  
**Policy:** archive, do not delete  
**Authority:** `docs/GITHUB_ESTATE_LEDGER.md` and `docs/REPOSITORY_LIFECYCLE_STANDARD.md`

## 1. `endgame-solutions/marion-county-weather-hub`

Lifecycle: duplicate maintenance candidate → superseded mirror → archive-ready.

### Evidence

- The live Lovable project is named `marioncounty-weather-wise` and is published publicly.
- `Stormchaser407/marioncounty-weather-wise` and `endgame-solutions/marion-county-weather-hub` were verified on 2026-08-19 to share the exact current HEAD `423a0f57865677c0c6b6eaa0bfea1914119e2f29`.
- Multiple immediately preceding Lovable-generated commits also share identical SHAs across both repositories, including commits carrying `X-Lovable-Edit-ID` metadata.
- The live Lovable project identity therefore matches the personal repository name, while the organization repository is a redundant Git mirror of the same implementation history.

### Disposition

Retain `Stormchaser407/marioncounty-weather-wise` as canonical GitHub source for the current Lovable-linked project. Archive `endgame-solutions/marion-county-weather-hub`. Do not delete it. Archival does not affect the published Lovable application.

## 2. `Stormchaser407/argus-reference`

Lifecycle: reference → archived static reference.

### Evidence

- Repository metadata identifies this as a sanitized standalone historical Project Argus reference tree.
- Current README describes a Telegram-derived investigative research implementation and GPL-3.0 licensing.
- No reference to `argus-reference` was found in current `Stormchaser407/homelab-nixos-config`.
- No canonical Cerberus runtime dependency on this repository was found.
- The repository remains useful as selectively reviewable historical research, but it does not need active-shelf status to remain cloneable, auditable, or available for future provenance-reviewed harvest.

### Disposition

Archive the repository as a static research/reference source. Do not delete it. Any future Cerberus harvest should explicitly unarchive or clone/read the archived source and independently review provenance, licensing, safety, and current architectural fit before reuse.

## Estate impact

If both GitHub archive flags verify successfully, the estate becomes **54 archived / 33 visible** out of the current 87-repository census.
