# Initial harvest — 2026-09-26

**28 upstream projects inspected; 90 individual core/subsystem records catalogued.** Twenty-seven projects contribute selected source records. DSP-RTL-Lib was inspected but its script-driven downstream cores were deferred. Mirror lookups and unharvested search hits are not counted. Some records are board/system references explicitly marked as such, not standalone portable IP.

The deliverable includes strict YAML/JSON Schema validation, duplicate/reference and evidence checks, an offline search CLI, generated index, tests, PR CI, scheduled link auditing, and agent/contributor instructions. No third-party code is included.

## Inspection method and limits

Canonical repositories were cloned into a temporary directory outside the knowledge base. Selected source APIs, imports/dependencies, license notices, documentation and relevant verification files were inspected at recorded commits. The [inspection manifest](inspection-manifest.json) records the selected source identities and SHA-256 hashes. It is a provenance aid, not a code audit certificate. Repository aliases preserve known moves.

This is source-level evaluation, not exhaustive RTL review. `evaluated` means a documented initial fit review. No target requirements were supplied for a specific MODULIQ/AI-HIL implementation, and no adoption is asserted. All `our_usage` arrays are empty. Unknown completeness, coverage and portability remain qualification work.

The environment had Python/YAML/schema support but no discovered HDL simulator or synthesis executable in PATH. No FPGA source was executed or built. Testbench inspection and committed upstream artifacts remain distinct from successful execution. Local tooling validation is recorded separately below.

## Coverage

| Ecosystem | Inspected projects | Core/subsystem records | Notes |
|---|---:|---:|---|
| Colibri | 1 | 22 | CDC, FIFO, SPI master/slave, I2C, UART, packet headers, stream buffer, Avalon-ST/AXI-Stream bridges, Wishbone RAM, CRC, gearbox, 8b/10b, frequency counter, RAM |
| LiteX / Enjoy Digital | 7 | 21 | Internal Wishbone/CSR/stream/peripherals plus LiteEth, LiteScope, LitePCIe, LiteDRAM, LiteJESD204, LiteICLink |
| ARTIQ / MiSoC / Phaser | 4 | 12 | RTIO/DRTIO, SPI/TTL/SERDES, EEM, Kasli/Kasli-SoC; MiSoC SPI/CORDIC; Phaser interpolation/IIR |
| CERN/OHWR timing and general cores | 5 | 8 | WRPC/endpoint, WREN pulser, SPEC/SPEC7, CIC/IQ/FIR |
| Red Pitaya / PyRPL / Linien / SingularitySurfer | 4 | 19 | PID, IQ, IIR, decimation, triggers, acquisition, autolock; lock-in chain and its extracted elements |
| Broader sweep | 7 | 8 | Taxi (3), legacy AXI/Ethernet (2), WB2AXIP (1), ZipCPU CORDIC (1), GibbleLab (1); DSP-RTL-Lib (0, deferred) |

## Most promising candidates for requirements-specific evaluation

- **Colibri stream/FIFO/bridge infrastructure:** per-component test coverage tables, VUnit test sources, selected formal properties and vendor import scripts provide useful starting evidence. Formal coverage is not uniform; RAM inference depends on implementation style. See [FIFO](../catalog/fifo/colibri-fifo.yaml), [RAM-backed asynchronous FIFO](../catalog/fifo/colibri-cc-ram-fifo.yaml) and [Avalon-ST to AXI-Stream](../catalog/bus/colibri-avst-to-axis.yaml).
- **LiteX internal stream/Wishbone and LiteEth:** useful ecosystem components with inspected simulation harnesses. [ECP5 RGMII](../catalog/ethernet/liteeth-ecp5-rgmii.yaml) has target-specific code and an available LiteX Yosys/nextpnr backend, but no synthesis pass is claimed here. [Etherbone](../catalog/bus/liteeth-etherbone.yaml) is a useful remote Wishbone candidate.
- **OHWR DSP and Phaser:** [CIC](../catalog/dsp/gc-cic.yaml), [IQ demodulator](../catalog/dsp/gc-iq-demodulator.yaml), and [Phaser interpolation](../catalog/dsp/phaser-interpolate.yaml) expose reusable functions; numerical behavior and dependencies require a target-specific test plan.
- **Linien:** [PID](../catalog/control/linien-pid.yaml) and [FPGA autolock](../catalog/control/linien-autolock.yaml) are more relevant than rebuilding a laser-lock chain from scratch. Host algorithms and gateware conventions remain coupled.
- **Taxi and WB2AXIP:** [Taxi asynchronous AXI FIFO](../catalog/fifo/taxi-axis-async-fifo.yaml) has a matching cocotb harness; [WB2AXIP bridge](../catalog/bus/wb2axip-bridge.yaml) has a parameterized formal configuration. Their licenses and evidence need separate evaluation; neither has been qualified locally.

## Negative knowledge and selection decisions

- **GibbleLab cavity PID:** rejected from the explicitly named *commercial-compatible evaluation shortlist* because the upstream README specifies CC-BY-NC-SA-3.0. This is a conditional reuse decision, not a statement that MODULIQ/AI-HIL has that policy. Retained for architectural study. [Record](../catalog/control/gibblelab-cavity-pid.yaml).
- **Legacy verilog-axis / verilog-ethernet:** reference-only because both upstreams explicitly direct future fixes to Taxi. Legacy MIT terms and Taxi's CERN-OHL-S/commercial offering are different; do not silently replace one license assumption with the other. [Project records](../projects/verilog-axis.yaml), [Taxi](../projects/taxi.yaml).
- **PyRPL:** root MIT notice and retained GPL-3.0-or-later RTL headers conflict. Selected blocks remain reference-only pending reconciliation; the MIT badge is not treated as permission for all RTL. [Project record](../projects/pyrpl.yaml).
- **MiSoC CORDIC:** GPL source notice differs from the repository BSD default. [Record](../catalog/dsp/misoc-cordic.yaml).
- **Colibri I2C:** no SCL input in the inspected entity; clock stretching cannot be observed. [Record](../catalog/i2c/colibri-i2c-controller.yaml).
- **Colibri CDC:** independent bit synchronizers do not guarantee coherent multi-bit words. Use a handshake or FIFO when needed; simulation does not establish physical metastability performance. [Record](../catalog/cdc/colibri-synchro.yaml).
- **Red Pitaya stream handling:** selected decimation sources retain TODOs around TLAST/TKEEP handling. Packet preservation is not established. [Record](../catalog/dsp/redpitaya-decimator.yaml).
- **SingularitySurfer:** the current top-level comments out historical CIC instances and uses RIIR. The RIIR tick handling needs review; the adapted CORDIC has limited iterations and third-party licensing to audit. The instrument remains an architectural reference. [Chain](../catalog/lockin/singularitysurfer-chain.yaml), [CIC](../catalog/dsp/singularitysurfer-cic.yaml), [IIR](../catalog/dsp/singularitysurfer-iir.yaml).
- **ARTIQ and carrier integrations:** RTIO/DRTIO, Kasli, Kasli-SoC and SPEC/SPEC7 are explicitly scoped systems/platforms. MiSoC SPI is a more direct extraction candidate than the RTIO wrapper for a non-ARTIQ design.
- **100BASE-FX:** no qualified standalone optical PCS was identified in this bounded harvest. RMII/MII/RGMII interfaces and a 1000BASE-X White Rabbit endpoint do not establish 100BASE-FX support. The search result records that distinction rather than an unsupported compatibility claim.

## Evidence not independently verified

No HDL simulation, formal proof, elaboration, synthesis, place-and-route, bitstream generation, hardware smoke test or HIL validation was performed locally. Upstream CI configuration was inspected, but no passing pipeline was adopted as a block-level result. No upstream build artifact is assumed to match its repository HEAD without a build manifest. The committed SingularitySurfer artifacts are `present`, not our reproduced passes.

CERN's WREN report describes about 50 nodes in pilot operational use. The system-level record preserves this as an upstream claim at unspecified revisions; its wiki also has testing-phase wording. Neither is propagated as independent validation of the extracted pulser. [CERN deployment report](https://ats-news.web.cern.ch/white-rabbit-event-node-deployment/), [WREN record](../projects/wren.yaml).

Most projects have unknown last meaningful activity because this pass did not classify full histories. Five have recent substantive changes inspected in sampled history; source-only/license-only changes and moving HEAD dates were not automatically equated with engineering maintenance. No abandoned status was invented from age alone.

## Tooling validation

- All 118 catalogue/project YAML records pass schema and semantic validation.
- Seventeen regression tests cover evidence laundering, stage independence, own-use/lifecycle claims, compatibility confidence, YAML duplicate keys, duplicate repositories/cores, missing references, search intersections, aliases, URL classifications and deterministic indexes.
- Search examples work, including `--fpga ecp5 --toolchain yosys ethernet`; results clearly say `integration_present`.
- Initial HTTP audit: 30 repository/alias URLs checked, 29 reachable and one known rename (LiteJESD204B → LiteJESD204). ARTIQ's GitHub page returns HTTP 200 while announcing a move; content inspection caught it. See [URL audit](url-check.json).
- Source evidence paths were checked against the pinned temporary checkouts. External wiki/news content can change and is access-dated. Full historical report preservation and content-aware move detection remain future improvements.

GitHub PR CI result will be linked from the draft PR once available. Catalogue checks do not validate the underlying FPGA implementations.

## Next harvesting and qualification work

1. Capture target constraints for MODULIQ/AI-HIL, then run small reproducible simulations and synthesis matrices for Colibri SPI/CDC/FIFO and LiteEth ECP5 RGMII. Record reset, backpressure, CDC constraints and resource/timing results per configuration.
2. Evaluate permissive and reciprocal-license DSP alternatives under the actual project's distribution requirements; resolve PyRPL notices upstream.
3. Inspect NIST digital-servo, LNLS DSP predecessors, more lock acquisition/servo designs, and arithmetic overflow/quantization tests. DSP-RTL-Lib downstream repositories need separate commit and license inspection.
4. Harvest external-PHY and optical 100BASE-FX paths, timestamp calibration, and full PHY/MAC integration evidence. Check supported line rates instead of grouping all optical Ethernet together.
5. Extend White Rabbit/ARTIQ evidence with exact supported board revisions, transceiver constraints, calibration procedures and durable CI/HIL artifacts; inspect additional generally reusable leaf blocks.
6. Expand JESD204B/C, PCIe, SERDES/64b66b and debug qualification on specific devices. Capture successful and failed upstream pipeline results rather than reading badges.
