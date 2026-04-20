# FPGA IP Integration Architecture Report

Target device: `low_power_reliable_fpga_next_gen`
Architecture goal: integrate high-performance IP blocks while tracking timing, clocking, reset, power, and constraint risks

## Summary

- IP blocks reviewed: 8
- Total modeled bandwidth: 682.0 Gbps
- Average modeled latency: 83.75 ns
- Total modeled area: 770.0 KLE
- Total modeled power: 5390.0 mW
- High-risk blocks: 2
- Blocks needing review: 1

## Highest Risk Blocks

### cxl_type3_endpoint (CXL)

- Risk score: 100 (high risk)
- Timing slack: -0.04 ns
- Clock domains: 3
- Reset domains: 3
- Constraint ready: False
- Review actions:
  - open timing-closure review before integration freeze
  - run CDC review for multi-clock integration
  - run RDC review for reset sequencing
  - complete generated-clock and IO constraint package
  - include power and thermal budget review
  - track as architecture-level integration risk

### high_speed_serial_transceiver (HSS)

- Risk score: 100 (high risk)
- Timing slack: -0.11 ns
- Clock domains: 4
- Reset domains: 3
- Constraint ready: False
- Review actions:
  - open timing-closure review before integration freeze
  - run CDC review for multi-clock integration
  - run RDC review for reset sequencing
  - complete generated-clock and IO constraint package
  - include power and thermal budget review
  - track as architecture-level integration risk

### packet_noc (NoC)

- Risk score: 51 (needs review)
- Timing slack: 0.02 ns
- Clock domains: 2
- Reset domains: 2
- Constraint ready: True
- Review actions:
  - watch near-zero timing slack during place and route
  - include power and thermal budget review
