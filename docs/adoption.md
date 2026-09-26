# Use from FPGA projects

This repository is persistent technical memory. Its own `AGENTS.md` governs work inside this checkout. To make the rule apply in another workspace, include this in that project's agent instructions:

> Before implementing reusable FPGA/gateware functionality, search `codex-hil/gateware-knowledge-base` (local checkout: `/home/codex-hil/gateware-knowledge-base`). Read matching core/project records and evidence. Prefer suitable maintained upstream IP with adequate verification. Record actual use, rejection reasons and useful new discoveries in the knowledge base. Implement new IP only after documenting why existing options are unsuitable.

Use an absolute path to the CLI from another checkout:

```sh
/home/codex-hil/gateware-knowledge-base/ip-search --hdl VHDL spi
```

If the knowledge base is unavailable, restore the checkout or explicitly record the search limitation. Never pretend a search was performed. Use a local branch or draft PR for updates discovered during development; preserve user changes. Cross-project histories and private validation reports should be referenced without publishing confidential design details.

The initial `our_usage` lists are deliberately empty: this harvest establishes no actual MODULIQ or AI-HIL integration. Project-specific decisions must name real target constraints, not assumed FPGA families or license policies.
