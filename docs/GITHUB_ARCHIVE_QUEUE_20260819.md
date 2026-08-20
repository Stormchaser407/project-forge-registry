# GitHub Archive Queue — 2026-08-19

**Status:** preservation notices prepared; repository-level archive flag remains to be applied  
**Policy:** archive, do not delete  
**Authority:** `docs/GITHUB_ESTATE_LEDGER.md` and `docs/REPOSITORY_LIFECYCLE_STANDARD.md`

Each repository below has been given a README-level archive/supersession/reference notice during the 2026-08-19 estate closeout. Git history and source remain preserved. GitHub archival is intentionally used as cold/read-only storage rather than destruction.

## Prepared archive queue

### Trivial / training / retired operating-system shells

1. `Stormchaser407/hello-world`
2. `Stormchaser407/recon`
3. `Stormchaser407/cerberus-vault`
4. `Stormchaser407/RedditBeacon`
5. `Stormchaser407/my-tools`
6. `Stormchaser407/desktop-tutorial`
7. `Stormchaser407/espanso-snippets`
8. `Stormchaser407/foundations-of-git-exercise-repo`
9. `Stormchaser407/CommandBoard`
10. `Stormchaser407/chaos-control-bridge`
11. `NOTEvil-Inc/notevil-c2-obsidian-bridge`
12. `endgame-solutions/obsidian-council`

### Historical mobile / Experience predecessors

13. `Stormchaser407/pixel-9-pro-xl-TWRP-experiment`
14. `Stormchaser407/cerberus-mgm-boot`
15. `Stormchaser407/NotEvil-neon-district`
16. `Stormchaser407/pixel-dual-esim-diagnostics`

### Cerberus preservation sources

17. `Stormchaser407/Cerberus`
18. `Stormchaser407/wraith`
19. `Stormchaser407/aegis`
20. `Stormchaser407/mavrakis`
21. `Stormchaser407/oren`
22. `Stormchaser407/cerberus-command`
23. `Stormchaser407/cerberus-recon`
24. `Stormchaser407/cerberus-eyes-on`
25. `endgame-solutions/cerberus-aegis`
26. `endgame-solutions/cerberus-recon`
27. `endgame-solutions/cerberus-watch`
28. `endgame-solutions/cerberus-agents`
29. `endgame-solutions/cerberus-project`
30. `endgame-solutions/cerberus-insights`

These repositories remain valid selective-harvest sources after archival. `Stormchaser407/CreeperBot5000` is deliberately excluded because current Cerberus lineage evidence identifies an uninspected local ancestor copy that must be reconciled by the future fleet census first.

### Endgame / web / architecture predecessors

31. `Stormchaser407/forge-os-endgame-edition`
32. `Stormchaser407/endgame-diagrams`
33. `Stormchaser407/endgametraining`
34. `Stormchaser407/endgame-website`
35. `Stormchaser407/01-website-brand`
36. `endgame-solutions/Endgame-Consultation`
37. `Stormchaser407/djfiddlesticks-website`
38. `endgame-solutions/Forge-Doctrine`

The published ChatGPT Sites are current public-web authority for Endgame and DJ Fiddlesticks. `djfiddlesticks-ops` remains DJ Fiddlesticks ecosystem coordination authority.

### Librarian / Intake / Studios parked sources

39. `Stormchaser407/media-dedupe`
40. `NOTEvil-Inc/notevil-total-evac`
41. `Stormchaser407/secure-edit-flow`
42. `Stormchaser407/your-video-guru`

These are archived as preserved incubation/reference sources. Their ideas may be harvested later by Endgame Librarian/Intake or Endgame Studios when real implementation reactivates those areas.

## Explicitly not in this archive queue

The following categories remain unarchived for a named reason:

- canonical/active or maintenance systems;
- legitimate incubators with independent future identity;
- vendor/reference forks awaiting local-delta or runtime-dependency audit;
- `CreeperBot5000`, awaiting fleet/local lineage inspection;
- `openclaw-workspace`, awaiting live OpenClaw dependency check;
- `Technical_Documents`, awaiting N5/Librarian migration;
- the Marion County weather personal duplicate, awaiting confirmation that no deployment/Lovable binding depends on that remote even though the current Git history matches the preferred organization-owned repo.

## Archive application

The current ChatGPT GitHub connector does not expose GitHub's repository-archive switch. The archive flag must therefore be applied through GitHub UI or an authenticated GitHub CLI/API session.

Example for one repository:

```bash
gh api --method PATCH repos/Stormchaser407/hello-world -f archived=true
```

Do not use `gh repo delete` as part of this cleanup.

## Reversibility

GitHub archival is reversible. If a later implementation mission genuinely needs to resume one of these repositories, unarchive it deliberately, record the reason in Project Forge, perform the bounded work, and return it to an explicit lifecycle state afterward.
