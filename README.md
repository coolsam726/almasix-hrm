# Almasix HRM

People operations on [Almasix](https://github.com/almasix-dev/almasix) and [Orbit](https://github.com/almasix-dev/almasix-orbit).

One panel covers the employee record, leave, time, hiring, reviews, and the later modules (onboarding, roster, request desk, career, training, surveys, employee voice, discipline, and a small assistant). What a person can open depends on their role: their own record, the people who report to them, or everyone.

This is an independent product. It does not reuse another HR system's source, schema, or name.

## Run

With sibling checkouts of Almasix, Conduit, and Orbit:

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
smith migrate --seed
smith serve
```

Sign in as `ada@northwind.test` / `secret` (administrator), `grace@northwind.test` (supervisor), or `alan@northwind.test` (employee).

Against published packages, `pip install -e ".[dev]"` is enough. `smith migrate --seed` still loads the sample company.

## Layout

- `app/domain/` — rules (who can see a record, leave days, workflow, punches)
- `app/orbit/hrm/` — the panel: resources, pages, widgets
- `app/http/api.py` — JSON for the same actions
- `docs/parity/` — checklist for the core modules
- `docs/advanced/` — specs for the modules that sit on the same platform

## Tests

```bash
pytest
```
