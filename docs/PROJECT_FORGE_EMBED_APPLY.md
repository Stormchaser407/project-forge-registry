# Project Forge Embed Apply

## Purpose

Embed apply is the approved phase that writes Project Forge marker files to selected clean repositories.

## Required Approval

The command requires both:

    --apply
    --confirm-apply

## Marker Files

For each approved repo, this phase writes:

    .project-forge.yml
    docs/PROJECT_FORGE.md

## Safety

Embed apply refuses to write when:

- the repo is dirty
- the repo is protected
- the repo is the Project Forge control repo
- the repo was not selected
- the repo is not eligible
- marker files already exist

It does not:

- push
- fetch
- add or modify remotes
- install packages
- create commits in external repos
- delete files

## Operator Rule

After apply, external repos will be dirty until the operator reviews and commits the marker files inside those repos.
