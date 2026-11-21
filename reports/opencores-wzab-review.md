# OpenCores and Wojciech Zabołotny follow-up

Reviewed 2026-09-26. This follow-up adds **12 project records and 15 individually inspected core/tool records**, bringing the catalogue to **40 projects and 105 cores/subsystems**. Review depth differs: six Git projects and two OpenCores projects have selected implementation review; four OpenCores projects have documentation or test-harness review with RTL extraction deferred. Counts do not imply independent qualification.

The author's GitHub identity is [wzab](https://github.com/wzab). The useful starting points are [wzab-hdl-library](https://github.com/wzab/wzab-hdl-library), [AGWB](https://github.com/wzab/agwb), and the [WZabISE GitLab group](https://gitlab.com/WZabISE). Individual files also credit other contributors, notably Marek Gumiński for the original Beneš concentrator; repository ownership is not original authorship of every component.

## Harvest and practical relevance

| Project | Inspected material / catalogue scope | Main finding |
|---|---|---|
| wzab-hdl-library | Seven components: single/multistep IIR, Xilinx and Intel JTAG–Wishbone, FIFO-to-UDP, VZMQ, LFSR | Useful instrumentation/debug building blocks. VZMQ is simulation infrastructure, not synthesizable transport. |
| AGWB | Register generator and Wishbone CDC | Good candidates for register maps and classic-cycle bus crossings. Generator/output/dependency licenses have different scopes. |
| E2Bus | Ethernet local-bus controller | Proof-of-concept architecture reference; unresolved controller and RAM licensing blocks confident adoption. |
| VEXTPROJ | AXI-Lite-to-Wishbone bridge | Small reusable bridge; independently exercise backpressure, simultaneous channels, reset and errors. |
| xconcentrator | Baseline-network data concentrator and checker | Promising sparse DAQ stream compaction. Checker accepts empty output; add count/nonempty checks before relying on it. |
| concentrator | Beneš core and testbench | Older reference, with newer xconcentrator linked upstream; source credits Marek Gumiński. Demo clock ratios/output ordering matter. |
| OpenCores I2C, SVN r76 | Master top-level source | Canonical Richard Herveille controller. Source says Wishbone B.2; byte/bit controllers and regression inspection remain incomplete. |
| OpenCores CORDIC, SVN r6 | cordic.v and tb_cordic.v | First-quadrant configurable CORDIC by Dale Drinkard. Full-circle wrapper needed; license unresolved in inspected files. |
| OpenCores heap_sorter, SVN r9 | Testbench and Python checker; project page | Timestamp sorting candidate. Checker tests ordering/count, not complete payload equivalence; Python 2 syntax. No new core record until canonical implementation is retrieved. |
| OpenCores versatile_fft, SVN r3 | Single-unit Octave reference recipe | Reference comparison opens vim; this is not an automated pass/fail regression. Canonical engine retrieval deferred. |
| OpenCores lateq, SVN r4 | Method description and source listing | Simulation-derived pipeline latency balancing; attractive for DSP chains. Implementation/generator retrieval deferred. |
| OpenCores FADE, SVN r49 | Description and version directory listing | Raw Ethernet acquisition with retransmission/jumbo variants. Nonrouted/private EtherType; not UDP/IP. Implementation retrieval deferred. |

The six Git snapshots and six native SVN revisions are pinned in `projects/`. [The follow-up manifest](opencores-wzab-manifest.json) records hashes of the 15 inspected core inputs. Test/doc evidence links live beside their individual facts. No third-party source is committed.

## Negative knowledge and selection boundaries

- AGWB's README describes GPL v2 while its generator header says LGPL V2. Generated output permission is separate, and the bundled Wishbone CDC has a CC0 notice. Do not collapse these into one permissive project license.
- The AGWB CDC supports classic single cycles and requires bus-skew constraints in both directions; it is not a generic pipelined Wishbone crossing.
- IIR single-step and multistep versions trade arithmetic resources against throughput/latency. The fixed-point package setup needs reconciliation, and the component's CC0/public-domain statement excludes a GPL dependency.
- Several files say only “Dual GPL/BSD” or “BSD”, without precise versions/clauses. `LicenseRef-*` records uncertainty instead of guessing SPDX permissions.
- E2Bus remains reference-only pending licensing and integration qualification. The older Beneš concentrator remains a reference while the scalable successor is evaluated. These are catalogue decisions, not invented MODULIQ/AI-HIL rejections.
- The CORDIC bench prints numerical failures without an established failing exit status. Increasing precision requires new arctangent tables; first-quadrant coverage does not validate a full-angle wrapper. SingularitySurfer's README spells the predecessor author's name differently; the canonical source says Dale Drinkard. Its wrapper's MIT notice does not resolve predecessor licensing.
- The FFT and IIR recipes' manual vim comparisons are recorded as such, not as simulation passes.
- FADE's description names an experimental jumbo directory while the current root lists a stable jumbo directory. Resolve this source/documentation mismatch before selecting a variant.

## Retrieval and verification limits

OpenCores intermittently returned HTTP 500 and TLS/connection timeouts. Successfully retrieved files are linked through native `/!svn/bc/<revision>/` baselines. Directory listings and selected documents were accessible even when implementation requests failed. Retrieval failure does not establish a missing core or abandoned project.

Historical `freecores/heap_sorter` and `freecores/versatile_fft` mirrors were inspected as discovery aids (commits `0d88220f2ec162d1806031be969a78e7af0ff36d` and `3db97f3a4f42a1fa75dc3ebd5101eede80053cc7`). Their layouts differ from current SVN. They were not substituted silently for canonical revisions or counted as additional upstream projects/qualified cores.

No HDL simulation, synthesis, formal proof, place-and-route, bitstream generation or hardware/HIL run was performed. FADE's board-operation statements remain upstream claims. No production use or local adoption was established; `our_usage` remains empty. Recent maintenance responsiveness and last meaningful upstream activity remain unknown.

The schema now supports explicit SVN revisions and unknown repository dates without weakening Git commit pinning. Search includes author names and accent normalization (`./ip-search Zabołotny` or `Zabolotny`). Validation covers 145 YAML records; 19 tooling tests pass. The generated index is refreshed. [The URL audit](url-check-opencores-wzab.json) separates transient/access failures from broken links; HTTP reachability is not verification evidence.

## Next focused work

1. Finish canonical RTL/dependency retrieval for heap_sorter, versatile_fft, lateq and FADE, preserving per-file license notices and RAM portability constraints.
2. Evaluate AGWB CDC and JTAG–Wishbone against a concrete target's constraints, reset behavior and bus semantics.
3. Add numerical assertions and failing exit codes to isolated IIR/FFT/CORDIC qualification harnesses; include saturation, quantization, corner inputs and complete payload checks for stream processors.
4. Inspect OpenCores I2C byte/bit controllers, selected configurations and issue reports before treating the historical controller's reputation as evidence for a new integration.
