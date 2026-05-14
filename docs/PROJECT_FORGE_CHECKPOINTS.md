# Project Forge Checkpoints

## Purpose

This repo uses regular checkpoints so work can stop safely without losing the thread.

A checkpoint means:

- tests pass
- safe project-sync runs
- canonical reports remain clean
- working tree is clean
- annotated checkpoint tag is created

## Command

Run:

    ./scripts/project-forge-checkpoint

With a label:

    ./scripts/project-forge-checkpoint phase-10-intake-design

## What It Does

1. Runs the test suite.
2. Runs the safe project-sync wrapper.
3. Checks canonical reports for dirt.
4. Checks full repo status.
5. Refuses to tag if the repo is dirty.
6. Creates an annotated tag if clean.

## Tag Format

Checkpoint tags look like:

    checkpoint-YYYYMMDD-HHMMSS-label

Example:

    checkpoint-20260514-031500-phase-10-intake-design

## When To Use

Use checkpoints:

- before starting a new phase
- after a successful phase
- before handing work to Codex
- after manual implementation blocks
- before stopping for the night
- when momentum is fading

## Important Rule

Do not tag dirty work.

If the checkpoint script refuses to tag, either commit the work or restore it first.

## Safe Daily Flow

    git status --short
    ./scripts/project-sync-safe
    ./scripts/project-forge-checkpoint manual

## Notes

Checkpoint tags are local until remotes are intentionally configured and push policy is approved.
