# Example Tcl-style notes for FPGA/ASIC architecture review.
# This is not tied to a vendor tool; it documents the constraint concepts
# this project tracks for architecture review and engineering documentation.

create_clock -name core_clk -period 2.500 [get_ports core_clk]
create_clock -name pcie_refclk -period 10.000 [get_ports pcie_refclk]
create_clock -name mem_clk -period 1.875 [get_ports mem_clk]

set_clock_groups -asynchronous \
  -group [get_clocks core_clk] \
  -group [get_clocks pcie_refclk] \
  -group [get_clocks mem_clk]

set_false_path -from [get_ports por_reset] -to [all_registers]

# Review checklist:
# - generated clocks for high-speed and memory interfaces
# - CDC paths crossing bridge logic
# - reset-domain crossings during link/PLL/boot sequencing
# - IO timing constraints for board-level interfaces
# - floorplan-sensitive routes for NoC and high-bandwidth IP
