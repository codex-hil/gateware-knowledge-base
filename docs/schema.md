# Schema and evidence model

[entry.schema.json](../schemas/entry.schema.json) validates both YAML record types. All objects reject unrecognized fields; dates and URLs are format-checked. `scripts/kb.py validate` also enforces references, category placement, unique IDs, canonical repository aliases, unique `(project, upstream_path)` core identities, and evidence semantics. Duplicate YAML keys are errors.

## Record organization

| Record | Required information |
|---|---|
| Project | ID/name, canonical repository and aliases, author/organization, exact inspected revision, inspection date/scope, license scope, maintenance, documentation, limitations, system verification, provenance |
| IP | ID/name, project reference, exact source path, functionality/category/tags, HDL, leaf license, interfaces, family/tool compatibility, reuse scope, lifecycle, completeness, documentation, verification, limitations, our usage, rejections, selection, review date |

Project references are mandatory normalization, not missing metadata: join them to obtain the canonical repository, revision, author and maintenance. `ip-search --json` returns the core together with repository, revision and maintenance. Core source paths identify a reusable block, a cohesive group in a single upstream file, or an explicitly marked system/board integration. Do not create several records with the same source identity just to increase counts.

`reuse_scope` is `general`, `ecosystem`, `platform`, or `system`. It describes coupling, not quality. `selection.status` is `candidate`, `reference_only`, `rejected`, or `selected`; a candidate is not approved for a specific project.

Licenses use SPDX expressions where established. `LicenseRef-*` labels describe unresolved/mixed scope, not new licenses or permissions. A root license does not erase more specific notices. Aliases preserve historical repository URLs, including moves that return HTTP 200 without redirecting.

Maintenance is `active`, `unknown`, `dormant`, `deprecated`, `archived`, or `moved`, with evidence. `observed_head_date` is repository metadata (or null if not established); it is not the last meaningful engineering change. `last_meaningful_activity` stays null unless a substantive HDL/test/integration change was reviewed. An `active` observation does not promise maintainer response times. Do not classify inactivity as abandonment without evidence.

## Independent verification facts

Every IP and project has all of these fields:

`source`, `elaboration`, `upstream_testbench`, `self_checking_testbench`, `simulation`, `formal`, `upstream_ci`, `synthesis`, `place_and_route`, `bitstream`, `hardware_smoke`, `functional_hil`, `independent_validation`, `production_deployment`.

Each fact has a status, summary and evidence array. Core records also list observed verification frameworks. A simulation result must name whether it covers generated RTL, a Migen model, or just host software.

| Status | Meaning |
|---|---|
| `unknown` | Not established; neither absent nor passing |
| `present` | Source, harness, recipe or artifact exists; no success implied |
| `claimed` | A party says the property/result holds; provenance identifies the party |
| `passed` / `failed` | A scoped result is backed by a run/report, not just configuration |
| `partial` | Coverage or implementation is explicitly incomplete |
| `not_supported` | Positive evidence of an unsupported feature |
| `not_applicable` | Evidence explains why this stage does not apply |

Non-unknown statuses require evidence. Result statuses cannot be supported solely by README claims or source inspection. The validator catches common evidence laundering; a reviewer still must judge whether the linked report actually supports its scope. No automated schema can establish that a report is truthful.

An evidence item records `type`, `url`, `accessed`, `scope`, and `details`; add exact `revision` for pinned source/results. Types distinguish `source_inspection`, `upstream_claim`, `upstream_ci`, `upstream_artifact`, `third_party_report`, `our_review`, and individual `our_*` run types. Our run evidence requires `report`, `revision` and `toolchain`; local report paths must exist inside the repository. Record FPGA/device and parameters for relevant runs. CI metadata should include the run URL and tested commit, not a branch badge.

`our_review` is an engineering inference/decision, not an executed test. `upstream_artifact` with `present` means an artifact exists; it does not prove that current source produced it. Project system evidence is not inherited by child cores.

## Compatibility and lifecycle

Family/toolchain entries have name, status, scope and evidence. Status is `claimed`, `integration_present`, `tested`, or `unsupported`. An existing Yosys backend does not establish synthesis of the selected core. A Verilator entry is simulation compatibility unless scope says otherwise. Unsupported entries never satisfy a compatibility search. Absent entries remain unknown; the CLI does not infer portability.

The lifecycle states are `discovered`, `evaluated`, `simulation-tested`, `synthesis-tested`, `hardware-tested`, `HIL-validated`, `production-used`. These summarize **our** latest activity, while all independent facts remain available. Later states do not fill earlier evidence automatically. Tested states require the corresponding own report; production use needs a scoped operational-use report. `our_usage` is a list of actual project/module/role/state records, not examples copied into real data.

`rejected_for` contains an actual project or explicitly named evaluation shortlist, the reason, date and evidence. Limitations distinguish bugs, unsupported modes, toolchain issues, architecture, maintenance, license, resources and verification gaps. Keep these findings when an alternative is chosen.

For a concrete example, inspect [Colibri SPI master](../catalog/spi/colibri-spi-master.yaml), [ECP5 RGMII](../catalog/ethernet/liteeth-ecp5-rgmii.yaml), and [the WREN system record](../projects/wren.yaml). Future schema changes must update documentation, migration guidance, semantic validation and tests together.

## Native SVN sources (backward-compatible schema extension)

Git records retain a full 40-hex commit and may omit `vcs` (default `git`). Native OpenCores records set `vcs: svn` and `revision: "svn:76"`, for example. Evidence URLs use Apache SVN baselines (`/!svn/bc/76/`) to pin source files. `HEAD` and unqualified SVN revision numbers are rejected. Existing Git records need no migration. A directory HTTP modification date is not automatically the last meaningful upstream activity, so unknown dates remain null.

Search includes project names and author/organization, with Unicode accent normalization, so `Zabolotny` and `Zabołotny` both find the author’s catalogued components. It returns core records; documentation-only discoveries remain visible in the project index.
