# Project Forge Follow-Up Signals

## Authority Contract

Project Forge detects and reports a technical follow-up signal. Master Scheduler
or the operator decides whether it becomes actionable. Todoist owns the
resulting actionable commitment.

A signal is technical evidence, not a task. Project Forge does not assign
personal priority, due dates, owners of personal commitments, or calendar time.
It does not silently create or synchronize Todoist items.

## Machine-Readable Record

The current bounded queue is `artifacts/technical_followup_signals.json`. Each
signal contains:

- `signal_id`: stable Project Forge evidence identifier
- `project_slug`: affected registry project, or `null` for a fleet-level signal
- `technical_condition`: concise observed condition
- `severity`: `low`, `medium`, `high`, or `critical`
- `evidence`: inspected paths, commits, reports, or command results
- `suggested_next_action`: a narrow technical recommendation
- `authority_destination`: the system or operator that may decide what happens
- `detected_at`: timestamp with timezone
- `status`: `open`, `acknowledged`, `exported`, or `resolved`

Evidence may include repository names and commit identifiers, but must not
contain credentials, personal contact/payment data, database contents, raw case
evidence, or protected-path contents.

## State Transitions

Project Forge may mark a signal `acknowledged`, `exported`, or `resolved` when
there is evidence for that state. Export means an authority received the signal;
it does not mean a Todoist commitment exists. Only Todoist is authoritative for
an actionable commitment.
