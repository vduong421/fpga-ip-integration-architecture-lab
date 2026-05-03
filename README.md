# FPGA IP Integration Architecture Lab

Project for entry-level FPGA architecture, ASIC/FPGA IP integration, hardware architecture, and EDA scripting roles.

This project models how multiple FPGA IP blocks can be compared and integrated into a product architecture. It does not claim production ASIC flow ownership. It is a project-based simulation that practices architecture tradeoffs, timing risk, clock-domain crossing risk, constraint readiness, and cross-functional reporting.

## Role Match

Best for jobs asking for:

- FPGA architecture
- ASIC/FPGA IP development and integration
- PCIe, CXL, DDR, NoC, high-speed serial interfaces, eNVM, eSRAM, parallel IO
- Synthesis, constraint management, place and route, timing closure, CDC/RDC awareness
- Python or Tcl scripting for EDA workflows
- Cross-functional architecture reporting

## Features

- Loads an FPGA IP catalog from JSON.
- Scores each IP block for performance, power, timing risk, CDC/RDC risk, constraint readiness, and integration complexity.
- Builds a product-level architecture summary for a selected set of IP blocks.
- Generates JSON and Markdown reports that explain tradeoffs and debug priorities.
- Includes sample Tcl-style constraint notes for EDA-flow familiarity.
- Includes tests for scoring, architecture summary, and report generation.

## Run

```powershell
python src/fpga_arch_lab.py --catalog data/ip_catalog.json --output output
```

## Test

```powershell
python -m pytest tests
```

## Example Output

The report identifies:

- highest-risk IP blocks
- timing-closure risk
- CDC/RDC risk
- constraint-readiness gaps
- architecture-level latency, bandwidth, area, and power summaries
- recommended next review actions

## Engineering Impact
- Built a Python FPGA IP integration architecture model that compares PCIe, CXL, DDR, NoC, high-speed serial, eNVM, eSRAM, and parallel IO blocks across latency, bandwidth, power, area, timing risk, and CDC/RDC risk.
- Modeled architecture-readiness checks for synthesis constraints, clock domains, reset domains, timing slack, and integration complexity to mirror FPGA/ASIC product planning discussions.
- Generated JSON and Markdown architecture reports that summarize IP tradeoffs, timing-closure risks, and cross-functional review actions.

## Project Workbench

Launch the production-style desktop workbench with:

```powershell
launch-workbench.bat
```

What it adds:

- Local-first AI copilot using `google/gemma-4-e4b` by default
- Operator-focused workbench for reviewing real project inputs and outputs
- System design, production-impact, and operational brief generation on demand
- Grounded responses based on this project's README, sample files, and deterministic outputs

