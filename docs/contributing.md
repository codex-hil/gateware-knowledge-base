# Adding or updating knowledge

1. Search existing records and repository aliases. Reuse the project identity when adding a leaf core.
2. Clone or inspect upstream outside this repository; capture canonical URL, commit and inspected files. Do not initialize arbitrary build scripts merely to inspect a project.
3. Create a project record and one core YAML per useful source identity, following the schema and existing records. Keep unknowns explicit. Describe parameters, dependencies and selection risks in plain language.
4. Link evidence to exact commits where possible. Label changing wiki pages with access date and scope. Do not turn an upstream claim into our result.
5. Write reproducible run reports under `reports/` when testing: upstream/dependency commits, tool versions, command, device, clock, parameters, seeds, exit status, resource/timing outcomes, logs, coverage limits and date. Large artifacts may live in durable CI storage, linked from the report.
6. Add real usage and rejection records in the same change as the investigation. A rejected core remains searchable. A newly discovered bug should include the triggering configuration and reproducer when available.
7. Validate, run tooling tests, regenerate the index, review the diff, and submit a PR. The generated index must be committed.

Prefer a small inspected addition over an automatic bulk import. Refresh moving URLs through review: HTTP redirects may indicate a rename, an authentication page or a bot challenge. The URL script reports those cases and does not mutate records. `--strict` returns failure for confirmed broken/moved URLs; access-denied and transient failures remain inconclusive.

The weekly workflow produces reports rather than silently changing assessments. An agent doing a later harvest should inspect the latest artifact and revisit stale evidence relevant to its task. Scheduling does not constitute continuing autonomous research.
