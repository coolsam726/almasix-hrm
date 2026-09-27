# Advanced modules

These modules are specified here, then implemented on the same access policy and workflow table. There is no external source of record for them.

## Onboarding and offboarding

Templates have a kind (`onboarding` or `offboarding`) and a list of tasks. An assignment starts `pending`, an administrator moves it to `active`, and it can be completed only after every task id is recorded. Documents are the task titles plus anything attached later through the template body.

## Request desk

An employee opens a request (hiring, resignation, IT, or HR) with a subject. They submit it. An administrator resolves it. Empty subjects are refused.

## Roster

A shift has optional person and location, a start, and an end. Publishing requires a person, a location, and an end after the start. Unassigned shifts stay unpublished.

## Career

A development plan is a non-empty goal on an employee. A 9-box placement stores performance and potential, each an integer 1, 2, or 3.

## Training

Courses can enroll an employee once. Completing the enrollment sets a certificate code `HRM-{course}-{employee}`.

## Surveys

A survey has a title and an audience. Each employee can answer once.

## Employee voice

A grievance has a type and a description. The employee submits it. An administrator resolves it.

## Discipline

An administrator opens a case with a summary and an investigator, assigns it, then closes it. The history is the workflow states plus the audit trail.

## Cross-cutting

- Audit events record hire, purge, and payroll-connector changes
- Assets have a name, a serial, and an optional employee
- Policies and document templates need a title (or name) and a body
- Scheduled reports use a cadence of daily, weekly, or monthly
- A payroll connector endpoint must be https. The export includes salary amounts only for someone who can read payroll. It does not calculate pay
- Authenticators use a 6-digit time-based code. Confirming the code marks the factor confirmed
- The assistant answers headcount, leave balance, reporting line, and payroll summary from data the caller can already read. It refuses any request to change records, and it refuses payroll questions when the caller cannot read payroll
