# Gateware / FPGA IP Knowledge Base

Search here before implementing reusable gateware. Evaluate suitable upstream IP, prefer maintained implementations with evidence appropriate to your requirements, and record why you select or reject them.

This is technical memory for MODULIQ, AI-HIL, ARTIQ/quantum control, instrumentation and DSP work. It records scoped evidence and negative findings, not quality scores. No third-party source code is vendored.

Start with the [generated catalogue](docs/index.md), [initial review](reports/initial-review.md), [schema guide](docs/schema.md), and [agent instructions](AGENTS.md).

## Use

Python 3.10 or newer is required. Install the two Python dependencies in your normal environment, preferably a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
./ip-search spi
./ip-search "100base fx"
./ip-search lockin
./ip-search --fpga ecp5 --toolchain yosys ethernet
./ip-search --hdl VHDL --license CERN-OHL-W fifo
./ip-search --verification formal=present
./ip-search --verification synthesis=passed --json
./ip-search --toolchain yosys --compatibility tested
```

The initial seed contains **28 inspected projects and 90 separately identified IP blocks or subsystems**. Those include tightly coupled board/system integrations marked as references. They are not 90 independently qualified drop-in cores. All adoption decisions still require application requirements and dependency review.

A toolchain match may mean an integration script exists. Use `--compatibility tested` to require result-backed compatibility. A bare `--verification synthesis` means `synthesis=passed`. The seed intentionally returns no synthesis passes. Empty family/toolchain lists mean unknown, not universal compatibility. Search includes reference-only and rejected entries so previous investigations remain visible.

## Maintain

```sh
python3 scripts/kb.py validate
python3 -m unittest discover -s tests -v
python3 scripts/kb.py index
python3 scripts/kb.py index --check
python3 scripts/check_urls.py
python3 scripts/check_urls.py --all-evidence --output reports/url-check-full.json
```

`projects/` holds canonical repositories, pinned revisions, authors, project-level maintenance and system evidence. `catalog/<category>/` holds core-level interfaces, license scope, verification, limitations and our usage. The schema is JSON Schema 2020-12; catalogue data is YAML. See [contributing](docs/contributing.md) for the update procedure and [adoption](docs/adoption.md) for using this memory from another project.

CI checks the data, evidence rules, duplicate identities, CLI behavior and generated index. A separate weekly URL workflow publishes an audit artifact. It becomes scheduled when present on the default branch. It never upgrades claims or rewrites canonical URLs automatically.

This repository validates **knowledge records**, not the HDL they describe. No local FPGA build, simulation or HIL run is claimed by the initial harvest.

The MIT license covers this repository's original tooling and catalogue text. Referenced upstream IP retains its own license; this repository grants no rights to those implementations.
