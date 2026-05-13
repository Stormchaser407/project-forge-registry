# Project Scan Report

## Scope

- Scan roots: /mnt/storage/Cole/Projects, /home/cole/Projects
- Projects scanned: 32
- Mode: dry-run only
- Project folders modified: none

## Summary

- Category `active_project`: 16
- Category `archive`: 1
- Category `lab`: 1
- Category `reconciliation_required`: 1
- Category `unknown`: 13
- Action `ignore`: 1
- Action `register_full`: 11
- Action `review_required`: 20

## Manual Review Needed

- `andclaw-comms`: contains_env_files, not_a_git_repo
- `archive`: not_a_git_repo, name_suggests_archive_or_duplicate
- `casebot_public_record_checks`: not_a_git_repo
- `Cerberus`: not_a_git_repo, cerberus_special_case_candidate, do_not_sync, cerberus_name_requires_manual_reconciliation_review
- `cerberus-mgm-boot`: cerberus_special_case_candidate, do_not_sync, cerberus_related_project_requires_manual_review
- `cerberus_case_workspace`: contains_env_files, cerberus_special_case_candidate, do_not_sync, cerberus_related_project_requires_manual_review
- `DJ_request_system`: contains_env_files
- `endgame-solutions`: not_a_git_repo
- `hermes-agent`: contains_env_files, contains_node_modules
- `HomeAssistant`: not_a_git_repo
- `Maltego`: not_a_git_repo
- `NOTEvil-Inc`: not_a_git_repo
- `pixel-root-lab`: not_a_git_repo
- `Primal`: not_a_git_repo
- `primal-web-app`: contains_env_files, contains_node_modules
- `SillyTavern`: contains_node_modules
- `Stormchaser407`: not_a_git_repo
- `tidal-hifi`: contains_node_modules
- `tidal-scrobble-cop`: not_a_git_repo

## Projects

| Folder | Slug | Stack | Status | Category | Action | Warnings |
| --- | --- | --- | --- | --- | --- | --- |
| AgentZero | agentzero | unknown | review | active_project | register_full | none |
| andclaw-comms | andclaw_comms | unknown | review | unknown | review_required | contains_env_files, not_a_git_repo |
| archive | archive | unknown | review | archive | ignore | not_a_git_repo, name_suggests_archive_or_duplicate |
| casebot_public_record_checks | casebot_public_record_checks | unknown | review | unknown | review_required | not_a_git_repo |
| Cerberus | cerberus | unknown | review | reconciliation_required | review_required | not_a_git_repo, cerberus_special_case_candidate, do_not_sync, cerberus_name_requires_manual_reconciliation_review |
| cerberus-mgm-boot | cerberus_mgm_boot | unknown | review | unknown | review_required | cerberus_special_case_candidate, do_not_sync, cerberus_related_project_requires_manual_review |
| cerberus_case_workspace | cerberus_case_workspace | python | review | unknown | review_required | contains_env_files, cerberus_special_case_candidate, do_not_sync, cerberus_related_project_requires_manual_review |
| DJ_request_system | dj_request_system | unknown | review | active_project | review_required | contains_env_files |
| endgame-solutions | endgame_solutions | unknown | review | unknown | review_required | not_a_git_repo |
| Extension-Blip | extension_blip | unknown | review | active_project | register_full | none |
| foundations-of-git-exercise-repo | foundations_of_git_exercise_repo | unknown | review | active_project | register_full | none |
| hermes-agent | hermes_agent | node, python, nix, docker | review | active_project | review_required | contains_env_files, contains_node_modules |
| HomeAssistant | homeassistant | unknown | review | unknown | review_required | not_a_git_repo |
| lifesaver-ledger | lifesaver_ledger | unknown | review | active_project | register_full | none |
| Maltego | maltego | unknown | review | unknown | review_required | not_a_git_repo |
| media-dedupe | media_dedupe | unknown | review | active_project | register_full | none |
| neon-district | neon_district | unknown | review | active_project | register_full | none |
| NOTEvil-Inc | notevil_inc | unknown | review | unknown | review_required | not_a_git_repo |
| openclaw-workspace | openclaw_workspace | unknown | review | unknown | review_required | none |
| pixel-root-lab | pixel_root_lab | unknown | review | lab | review_required | not_a_git_repo |
| Primal | primal | unknown | review | unknown | review_required | not_a_git_repo |
| primal-web-app | primal_web_app | node | review | active_project | review_required | contains_env_files, contains_node_modules |
| project-forge-registry | project_forge_registry | python | review | active_project | register_full | none |
| project_katrina | project_katrina | unknown | review | unknown | review_required | none |
| recon_housekeeping | recon_housekeeping | unknown | review | active_project | register_full | none |
| SillyTavern | sillytavern | node | review | active_project | review_required | contains_node_modules |
| SpiderFoot_PeopleSearch | spiderfoot_peoplesearch | unknown | review | active_project | register_full | none |
| SteelSeries_RGB | steelseries_rgb | unknown | review | active_project | register_full | none |
| Stormchaser407 | stormchaser407 | unknown | review | unknown | review_required | not_a_git_repo |
| this-was-avoidable | this_was_avoidable | unknown | review | active_project | register_full | none |
| tidal-hifi | tidal_hifi | node | review | active_project | review_required | contains_node_modules |
| tidal-scrobble-cop | tidal_scrobble_cop | unknown | review | unknown | review_required | not_a_git_repo |
