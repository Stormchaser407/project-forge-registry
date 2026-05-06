# Cerberus Archaeology Report

Generated: Wed May  6 02:44:26 PM EDT 2026

## Purpose

Read-only comparison of Cerberus folders before any reconciliation, deletion, move, registry promotion, or sync automation.

## Paths

- Home canonical candidate: `/home/cole/cerberus`
- Storage reconciliation candidate: `/mnt/storage/Cole/cerberus`

## Existence Check

- EXISTS: `/home/cole/cerberus`
- EXISTS: `/mnt/storage/Cole/cerberus`

## Top-Level Tree: Home Cerberus

```text
d ./ai
d ./ai/embeddings
d ./ai/models
d ./containers
d ./containers/minio
d ./containers/openclaw
d ./containers/spiderfoot
d ./containers/spiderfoot-image
d ./containers/systemd
d ./exports
d ./.git
d ./logs
d ./notes
d ./notes/field-notes
d ./notes/obsidian
d ./projects
d ./proxy
d ./proxy/__pycache__
d ./recon
d ./recon/cases
d ./recon/exports
d ./recon/raw
d ./recon/scripts
d ./recon/spiderfoot-image-build
d ./recon/spiderfoot.migrated-backup-20260506-000108
d ./runbooks
d ./scripts
d ./scripts/__pycache__
d ./searxng
d ./searxng/config
f ./ai/.directory
f ./containers/.directory
f ./.directory
f ./exports/.directory
f ./.gitignore
f ./logs/.directory
f ./notes/.directory
f ./projects/.directory
f ./proxy/.directory
f ./proxy/proxy.py
f ./README.md
f ./recon/.directory
f ./runbooks/BACKUP_RESTORE.md
f ./runbooks/codex-consolidation-summary.txt
f ./runbooks/codex-overnight-summary.txt
f ./runbooks/codex-recon-changes.txt
f ./runbooks/codex-recon-findings.txt
f ./runbooks/.directory
f ./runbooks/MASTER_STATUS_BOARD.md
f ./runbooks/MIGRATION_BACKLOG.md
f ./runbooks/NEXT_ACTIONS.md
f ./runbooks/RECON_OPERATIONS.md
f ./runbooks/SERVICE_MODEL.md
f ./runbooks/spiderfoot.md
f ./runbooks/storage-plan.md
f ./runbooks/system_snapshot.txt
f ./runbooks/VALIDATION.md
f ./runbooks/WORKSPACE_MAP.md
f ./scripts/.directory
f ./scripts/install-user-units.sh
f ./scripts/mainstream_listener.py
f ./scripts/snapshot-live-units.sh
f ./scripts/validate-recon.sh
f ./searxng/.directory
l ./recon/spiderfoot
```

## Top-Level Tree: Storage Cerberus

```text
d ./ai
d ./ai/embeddings
d ./ai/models
d ./containers
d ./containers/minio
d ./containers/openclaw
d ./containers/spiderfoot
d ./containers/spiderfoot-image
d ./containers/systemd
d ./exports
d ./.git
d ./notes
d ./notes/field-notes
d ./notes/obsidian
d ./projects
d ./proxy
d ./proxy/__pycache__
d ./recon
d ./recon/cases
d ./recon/exports
d ./recon/raw
d ./recon/scripts
d ./recon/spiderfoot
d ./runbooks
d ./scripts
d ./searxng
d ./searxng/config
f ./ai/.directory
f ./containers/.directory
f ./.directory
f ./exports/.directory
f ./.gitignore
f ./notes/.directory
f ./projects/.directory
f ./proxy/.directory
f ./proxy/proxy.py
f ./README.md
f ./recon/.directory
f ./runbooks/BACKUP_RESTORE.md
f ./runbooks/codex-consolidation-summary.txt
f ./runbooks/codex-overnight-summary.txt
f ./runbooks/codex-recon-changes.txt
f ./runbooks/codex-recon-findings.txt
f ./runbooks/.directory
f ./runbooks/MASTER_STATUS_BOARD.md
f ./runbooks/MIGRATION_BACKLOG.md
f ./runbooks/NEXT_ACTIONS.md
f ./runbooks/RECON_OPERATIONS.md
f ./runbooks/SERVICE_MODEL.md
f ./runbooks/spiderfoot.md
f ./runbooks/storage-plan.md
f ./runbooks/system_snapshot.txt
f ./runbooks/VALIDATION.md
f ./runbooks/WORKSPACE_MAP.md
f ./scripts/.directory
f ./scripts/install-user-units.sh
f ./scripts/snapshot-live-units.sh
f ./scripts/validate-recon.sh
f ./searxng/.directory
```

## Git Status: Home Cerberus

```text
Branch: codex/recon-consolidation-pass

?? recon/
?? searxng/config/settings.yml.new

Recent commits:
a65ba94 Refine recon service wrappers and docs
f8f2eff Consolidate Recon repo docs and scripts
5cb333a Reconcile Recon repo with live container model
cec9d71 Add live user systemd container units from Recon
692f631 Initial Recon workspace snapshot

Remotes:
codeberg	https://codeberg.org/stormchaser/Stormchaser407-cerberus-recon.git (fetch)
codeberg	https://codeberg.org/stormchaser/Stormchaser407-cerberus-recon.git (push)
origin	https://github.com/Stormchaser407/cerberus-recon.git (fetch)
origin	https://github.com/Stormchaser407/cerberus-recon.git (push)
```

## Git Status: Storage Cerberus

```text
Branch: codex/recon-consolidation-pass

?? .directory
?? ai/
?? containers/.directory
?? containers/minio/
?? containers/openclaw/
?? containers/spiderfoot-image/.directory
?? containers/spiderfoot/
?? containers/systemd/.directory
?? containers/systemd/intended/
?? containers/systemd/live/
?? exports/
?? notes/
?? projects/
?? proxy/.directory
?? recon/
?? runbooks/.directory
?? scripts/.directory
?? searxng/.directory
?? searxng/config/.directory

Recent commits:
f8f2eff Consolidate Recon repo docs and scripts
5cb333a Reconcile Recon repo with live container model
cec9d71 Add live user systemd container units from Recon
692f631 Initial Recon workspace snapshot

Remotes:
origin	https://github.com/Stormchaser407/cerberus-recon.git (fetch)
origin	https://github.com/Stormchaser407/cerberus-recon.git (push)
```

## Storage-Only Files Compared to Home

```text
sending incremental file list
./
ai/
ai/embeddings/
ai/models/
containers/
containers/minio/
containers/openclaw/
containers/spiderfoot-image/
containers/spiderfoot/
containers/systemd/
containers/systemd/intended/
containers/systemd/live/
exports/
notes/
notes/field-notes/
notes/obsidian/
projects/
proxy/
recon/
recon/cases/
recon/exports/
recon/raw/
recon/scripts/
runbooks/
scripts/
searxng/
searxng/config/
searxng/config/.directory

sent 2,659 bytes  received 127 bytes  5,572.00 bytes/sec
total size is 93,134  speedup is 33.43 (DRY RUN)
```

## Home-Only Files Compared to Storage

```text
sending incremental file list
./
ai/
ai/embeddings/
ai/models/
containers/
containers/minio/
containers/openclaw/
containers/spiderfoot-image/
containers/spiderfoot/
containers/systemd/
containers/systemd/mainstream-buttons.live.service
containers/systemd/mainstream-buttons.service
containers/systemd/intended/
containers/systemd/live/
exports/
logs/
logs/.directory
notes/
notes/field-notes/
notes/obsidian/
projects/
proxy/
recon/
recon/cases/
recon/exports/
recon/raw/
recon/scripts/
recon/spiderfoot-image-build/
recon/spiderfoot-image-build/Containerfile
recon/spiderfoot-image-build/Containerfile.bak-pip-upgrade-20260505-232220
recon/spiderfoot.migrated-backup-20260506-000108/
recon/spiderfoot.migrated-backup-20260506-000108/.directory
runbooks/
scripts/
scripts/mainstream_listener.py
searxng/
searxng/config/
searxng/config/settings.yml.new

sent 3,183 bytes  received 159 bytes  6,684.00 bytes/sec
total size is 164,134  speedup is 49.11 (DRY RUN)
```

## Important File Types Found


### /home/cole/cerberus

```text
./proxy/proxy.py
./README.md
./runbooks/BACKUP_RESTORE.md
./runbooks/MASTER_STATUS_BOARD.md
./runbooks/MIGRATION_BACKLOG.md
./runbooks/NEXT_ACTIONS.md
./runbooks/RECON_OPERATIONS.md
./runbooks/SERVICE_MODEL.md
./runbooks/spiderfoot.md
./runbooks/storage-plan.md
./runbooks/VALIDATION.md
./runbooks/WORKSPACE_MAP.md
./scripts/install-user-units.sh
./scripts/mainstream_listener.py
./scripts/snapshot-live-units.sh
./scripts/validate-recon.sh
./searxng/config/settings.yml
```

### /mnt/storage/Cole/cerberus

```text
./proxy/proxy.py
./README.md
./runbooks/BACKUP_RESTORE.md
./runbooks/MASTER_STATUS_BOARD.md
./runbooks/MIGRATION_BACKLOG.md
./runbooks/NEXT_ACTIONS.md
./runbooks/RECON_OPERATIONS.md
./runbooks/SERVICE_MODEL.md
./runbooks/spiderfoot.md
./runbooks/storage-plan.md
./runbooks/VALIDATION.md
./runbooks/WORKSPACE_MAP.md
./scripts/install-user-units.sh
./scripts/snapshot-live-units.sh
./scripts/validate-recon.sh
./searxng/config/settings.yml
```

## References to Cerberus in NixOS Config

```text
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-231035:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-231035:38:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/shell.nix.bak.2026-04-19-082951:12:      osint = "cd /home/cole/cerberus/recon/cases";
/etc/nixos/home/cole/modules/shell.nix.bak.2026-04-19-082951:13:      ai = "cd /home/cole/cerberus/ai";
/etc/nixos/home/cole/modules/shell.nix.bak.2026-04-19-082951:24:      capture = "sudo tcpdump -i any -w /home/cole/cerberus/recon/raw/capture_$(date +%F_%H%M).pcap";
/etc/nixos/home/cole/modules/wrappers.nix.bak-real-spiderfoot-root-mount-20260506-005359:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-real-spiderfoot-root-mount-20260506-005359:38:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix:38:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-230539:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-230539:44:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-230539:68:        -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/home/cole/modules/shell.nix:21:      osint = "cd /home/cole/cerberus/recon/cases";
/etc/nixos/home/cole/modules/shell.nix:22:      ai = "cd /home/cole/cerberus/ai";
/etc/nixos/home/cole/modules/shell.nix:33:      capture = "sudo tcpdump -i any -w /home/cole/cerberus/recon/raw/capture_$(date +%F_%H%M).pcap";
/etc/nixos/home/cole/modules/wrappers.nix.bak-spiderfoot-localhost-20260505-232509:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-spiderfoot-localhost-20260505-232509:38:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix.bak-spiderfoot-localhost-20260505-232509:54:        -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/home/cole/modules/wrappers.nix.bak-podman-external-20260505-230354:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-podman-external-20260505-230354:40:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix.bak-podman-external-20260505-230354:60:        -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/home/cole/modules/packages.nix.bak.2026-04-19-082951:27:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/packages.nix.bak.2026-04-19-082951:44:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/packages.nix.bak.2026-04-19-082951:64:        -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-231035.bak-spiderfoot-root-mount-20260506-005238:23:      exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-231035.bak-spiderfoot-root-mount-20260506-005238:38:        -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/home/cole/modules/wrappers.nix.bak-run-replace-20260505-231035.bak-spiderfoot-root-mount-20260506-005238:54:        -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/config_backups/backup-2026-04-12_164918/users.nix:45:    osint = "cd /home/cole/cerberus/recon/cases";
/etc/nixos/config_backups/backup-2026-04-12_164918/users.nix:46:    ai = "cd /home/cole/cerberus/ai";
/etc/nixos/config_backups/backup-2026-04-12_164918/users.nix:55:    capture = "sudo tcpdump -i any -w /home/cole/cerberus/recon/raw/capture_$(date +%F_%H%M).pcap";
/etc/nixos/archive/pristine-pass-2026-04-10-223804/configuration.nix.bak.2026-04-10-213424:10:- storage-and-tmpfiles.nix: mounts, zram, tmpfiles, cerberus directories, post-mount storage folder creation
/etc/nixos/archive/pristine-pass-2026-04-10-223804/configuration.nix.bak.2026-04-10-220908:10:- storage-and-tmpfiles.nix: mounts, zram, tmpfiles, cerberus directories, post-mount storage folder creation
/etc/nixos/archive/pristine-pass-2026-04-10-223804/configuration.nix.bak.2026-04-10-214526:10:- storage-and-tmpfiles.nix: mounts, zram, tmpfiles, cerberus directories, post-mount storage folder creation
/etc/nixos/archive/pristine-pass-2026-04-10-223804/configuration.nix.bak.2026-04-10-213527:10:- storage-and-tmpfiles.nix: mounts, zram, tmpfiles, cerberus directories, post-mount storage folder creation
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/configuration.nix:10:- storage-and-tmpfiles.nix: mounts, zram, tmpfiles, cerberus directories, post-mount storage folder creation
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/users.nix:45:    osint = "cd /home/cole/cerberus/recon/cases";
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/users.nix:46:    ai = "cd /home/cole/cerberus/ai";
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/users.nix:48:    capture = "sudo tcpdump -i any -w /home/cole/cerberus/recon/raw/capture_$(date +%F_%H%M).pcap";
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:22:    "d /home/cole/cerberus 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:23:    "d /home/cole/cerberus/recon 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:24:    "d /home/cole/cerberus/recon/cases 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:25:    "d /home/cole/cerberus/recon/raw 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:26:    "d /home/cole/cerberus/recon/exports 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:28:    "d /home/cole/cerberus/ai 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:29:    "d /home/cole/cerberus/ai/models 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:30:    "d /home/cole/cerberus/containers 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:31:    "d /home/cole/cerberus/containers/systemd 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:32:    "d /home/cole/cerberus/notes 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:33:    "d /home/cole/cerberus/runbooks 0755 cole users - -"
/etc/nixos/archive/pristine-pass-2026-04-10-223804/live/modules/storage-and-tmpfiles.nix:34:    "d /home/cole/cerberus/recon/scripts 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:5:    "d /home/cole/cerberus 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:6:    "d /home/cole/cerberus/recon 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:7:    "d /home/cole/cerberus/recon/cases 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:8:    "d /home/cole/cerberus/recon/raw 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:9:    "d /home/cole/cerberus/recon/exports 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:11:    "d /home/cole/cerberus/ai 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:12:    "d /home/cole/cerberus/ai/models 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:13:    "d /home/cole/cerberus/containers 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:14:    "d /home/cole/cerberus/containers/systemd 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:15:    "d /home/cole/cerberus/notes 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:16:    "d /home/cole/cerberus/runbooks 0755 cole users - -"
/etc/nixos/modules/storage/state.nix:17:    "d /home/cole/cerberus/recon/scripts 0755 cole users - -"
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:714:match ftp m|^220-Cerberus FTP Server Personal Edition\r\n220-UNREGISTERED\r\n| p/Cerberus FTP Server/ i/Personal Edition; Unregistered/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:715:match ftp m|^220-Cerberus FTP Server - Personal Edition\r\n220-This is the UNLICENSED personal edition and may be used for home, personal use only\r\n220-Welcome to Cerberus FTP Server\r\n220 Created by Cerberus, LLC\r\n| p/Cerberus FTP Server/ i/Personal Edition; Unregistered/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:716:match ftp m|^220-Cerberus FTP Server - Personal Edition\r\n220-This is the UNLICENSED personal edition and may be used for home, personal use only\r\n220 Connected to Aurora FTP server\.\.\.\r\n| p/Cerberus FTP Server/ i/Personal Edition; Unregistered/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:717:match ftp m|^220-Cerberus FTP Server - Personal Edition\r\n220-UNREGISTERED\r\n220-Welcome to Cerberus FTP Server\r\n220 Created by Grant Averett\r\n| p/Cerberus FTP Server/ i/Personal Edition; Unregistered/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:718:match ftp m|^220-Welcome to Cerberus FTP Server\r\n220 Created by Grant Averett\r\n| p/Cerberus ftpd/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:719:match ftp m|^421-Not currently accepting logins at this address\. Try back \r\n421 later\.\r\n| p/Cerberus ftpd/ i/banned/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:720:match ftp m|^220 Welkom@([\w._-]+)\r\n521 Not logged in - Secure authentication required\r\n| p/Cerberus ftpd/ o/Windows/ h/$1/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:1251:match ftp m|^220-Cerberus FTP Server - Home Edition\r\n220-This is the UNLICENSED Home Edition and may be used for home, personal use only\r\n220-Welcome to Cerberus FTP Server\r\n220 Created by Cerberus, LLC\r\n| p/Cerberus FTP Server/ i/Home Edition/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:1252:match ftp m|^220-220-Welcome to Cerberus FTP Server\r\n220 220 Created by Cerberus, LLC\r\n| p/Cerberus FTP Server/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:1253:match ftp m|^220-Welcome to Cerberus FTP Server\r\n220 Created by Cerberus, LLC\r\n| p/Cerberus FTP Server/ o/Windows/ cpe:/a:cerberusftp:ftp_server/ cpe:/o:microsoft:windows/a
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:3725:match ssh m|^SSH-([\d.]+)-CerberusFTPServer_([\w._-]+)\r\n| p/Cerberus FTP Server sshd/ v/$2/ i/protocol $1/ cpe:/a:cerberusftp:ftp_server:$2/
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:3726:match ssh m|^SSH-([\d.]+)-CerberusFTPServer_([\w._-]+) FIPS\r\n| p/Cerberus FTP Server sshd/ v/$2/ i/protocol $1; FIPS/ cpe:/a:cerberusftp:ftp_server:$2/
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nmap-service-probes:10586:match http m|^HTTP/1\.0 302 Redirected\r\nServer: CerberusFTPServer/([\d.]+)\r\n| p/Cerberus FTP Server httpd/ v/$1/ cpe:/a:cerberusftp:ftp_server:$1/
/etc/nixos/result/etc/profiles/per-user/cole/share/nmap/nselib/data/wp-plugins.lst:50300:mythic-cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/scummvm/pred.dic:431:23723787 cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/test/modules/auxiliary/test/report_auth_info.rb:343:  def test_cerberus_sftp_enumusers
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/test/modules/auxiliary/test/report_auth_info.rb:344:    mod = framework.auxiliary.create('scanner/ssh/cerberus_sftp_enumusers')
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/exploit/linux/http/acronis_cyber_infra_cve_2023_45249.md:205:SHA256:H1Ewu7NLZdYIV4SQZPhsaGkXb/IG9fQgZEjqfKBRTIg root@cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/exploit/multi/http/wp_plugin_fma_shortcode_unauth_rce.md:268:Linux cerberus 5.15.44-Re4son-v8l+ #1 SMP PREEMPT Debian kali-pi (2022-07-03) aarch64 GNU/Linux
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/exploit/multi/http/geoserver_unauth_rce_cve_2024_36401.md:190:Linux cerberus 5.15.44-Re4son-v8l+ #1 SMP PREEMPT Debian kali-pi (2022-07-11) aarch64 GNU/Linux
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/exploit/unix/webapp/openmediavault_auth_cron_rce.md:241:Linux cerberus 5.15.44-Re4son-v8l+ #1 SMP PREEMPT Debian kali-pi (2022-07-03) aarch64 GNU/Linux
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:22:2. ```use auxiliary/gather/cerberus_helpdesk_hash_disclosure```
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:31:    msf > use auxiliary/gather/cerberus_helpdesk_hash_disclosure
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:32:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > set rhosts 1.1.1.1
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:34:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > run
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:57:    msf > use auxiliary/gather/cerberus_helpdesk_hash_disclosure 
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:58:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > set rhosts 192.168.2.45
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:60:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > set targeturi /cerb5/
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:62:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > set verbose true
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/documentation/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.md:64:    msf auxiliary(cerberus_helpdesk_hash_disclosure) > run
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/data/wmap/wmap_dirs.txt:733:cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/data/wordlists/wp-plugins.txt:53269:mythic-cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/data/wordlists/password.lst:12214:cerberus
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:18103:  "auxiliary_gather/cerberus_helpdesk_hash_disclosure": {
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:18105:    "fullname": "auxiliary/gather/cerberus_helpdesk_hash_disclosure",
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:18138:    "path": "/modules/auxiliary/gather/cerberus_helpdesk_hash_disclosure.rb",
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:18140:    "ref_name": "gather/cerberus_helpdesk_hash_disclosure",
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:49949:  "auxiliary_scanner/ssh/cerberus_sftp_enumusers": {
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:49951:    "fullname": "auxiliary/scanner/ssh/cerberus_sftp_enumusers",
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:49972:    "path": "/modules/auxiliary/scanner/ssh/cerberus_sftp_enumusers.rb",
/etc/nixos/result/etc/profiles/per-user/cole/share/msf/db/modules_metadata_base.json:49974:    "ref_name": "scanner/ssh/cerberus_sftp_enumusers",
/etc/nixos/result/etc/profiles/per-user/cole/lib/python3.13/site-packages/theHarvester/data/wordlists/dns-names.txt:2238:cerberus
/etc/nixos/result/etc/profiles/per-user/cole/lib/python3.13/site-packages/theHarvester/data/wordlists/names_small.txt:5547:cerberus100
/etc/nixos/result/etc/profiles/per-user/cole/lib/python3.13/site-packages/theHarvester/data/wordlists/dns-big.txt:2238:cerberus
/etc/nixos/result/etc/profiles/per-user/cole/bin/searxng-container:15:  -v /home/cole/cerberus/searxng/config:/etc/searxng \
/etc/nixos/result/etc/profiles/per-user/cole/bin/spiderfoot-container:15:  -v /home/cole/cerberus/recon/spiderfoot:/data \
/etc/nixos/result/etc/profiles/per-user/cole/bin/mainstream-buttons:8:exec python3 /home/cole/cerberus/scripts/mainstream_listener.py
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:4:d /home/cole/cerberus 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:5:d /home/cole/cerberus/recon 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:6:d /home/cole/cerberus/recon/cases 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:7:d /home/cole/cerberus/recon/raw 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:8:d /home/cole/cerberus/recon/exports 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:9:d /home/cole/cerberus/recon/spiderfoot 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:10:d /home/cole/cerberus/ai 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:11:d /home/cole/cerberus/ai/models 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:12:d /home/cole/cerberus/containers 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:13:d /home/cole/cerberus/containers/systemd 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:14:d /home/cole/cerberus/notes 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:15:d /home/cole/cerberus/runbooks 0755 cole users - -
/etc/nixos/result/etc/tmpfiles.d/00-nixos.conf:16:d /home/cole/cerberus/recon/scripts 0755 cole users - -
```

## Initial Recommendation

- Treat `/home/cole/cerberus` as canonical until path dependencies are removed or rewritten.
- Treat `/mnt/storage/Cole/cerberus` as reconciliation-required.
- Do not bulk-register or sync either path until this report is reviewed.
- Add `system_bound_project` and `reconciliation_required` classifications to the project registry.
