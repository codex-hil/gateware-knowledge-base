# Gateware knowledge workflow

Before implementing reusable gateware, search the Gateware Knowledge Base. Prefer suitable existing and adequately verified upstream IP over reimplementation. If an existing core is rejected, record why. If new reusable IP or a useful upstream project is discovered during normal development, add it here.

1. Search functionality and synonyms with `./ip-search`; apply FPGA, toolchain, language and license filters when known. Read the YAML and its project record, not just search summaries.
2. Compare interface semantics, clock/reset behavior, throughput/latency, arithmetic precision, resources, board/PHY requirements, licenses and maintenance against the actual project. Unknown is not a pass or a failure.
3. Inspect canonical upstream at a pinned revision, including leaf-core licenses and dependencies. Follow recorded moves. A permissive repository badge does not override a conflicting file notice.
4. Prefer an appropriate maintained implementation with verification evidence that covers the intended configuration. Verify integration locally before advancing our lifecycle or claiming use.
5. Record selection in `selection`, project adoption in `our_usage`, and concrete rejection in `rejected_for`, with evidence and scope. Never invent MODULIQ/AI-HIL deployments. A shortlist decision is distinct from adoption.
6. If existing solutions are unsuitable, document the comparison and implement the missing functionality. Catalogue the new reusable block with its actual evidence.
7. Add useful discoveries during normal FPGA development. Preserve bugs, unsupported modes, incompatible licenses, resource issues, failed builds and superseded alternatives rather than deleting inconvenient results.

Evidence rules:

- Distinguish source inspection, upstream claims, CI results, third-party reports and our own simulations/builds/hardware/HIL runs.
- A testbench or CI configuration is `present`, not `passed`. A README assertion is `claimed`.
- Each verification stage is independent. Formal proof does not establish timing closure or hardware behavior; a bitstream does not establish a functional test.
- Record revision, tool/version, device/configuration, command and durable report for our runs. Preserve failed runs with the same care as passes. Never change `our_usage` merely because an author reports a deployment.
- Scope system evidence to the project. Do not propagate it to every leaf core. Record exact parameter coverage and dependency versions in reports.
- Do not vendor third-party code for cataloguing. Use canonical source links at exact commits and retained evidence reports; keep temporary inspection clones outside this repository.
- Do not treat the example evidence ladder as a numeric quality score or an implication chain.

After edits, run `python3 scripts/kb.py validate`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/kb.py index`. Commit regenerated indexes with the records. Use `scripts/check_urls.py` when sources change; classify access failures separately from broken links. Refresh dates only for material actually inspected.
