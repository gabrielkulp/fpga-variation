# Proposal: Dynamic Spatial Timing Analysis Across FPGA Elements

ECE 579, January 24, 2022.
Gabriel Kulp, Matthew Phillips.


## Motivation
Lowering the clock speed of RTL (register-transfer level) hardware designs is an aggressive form of error prevention, applied after making many assumptions about the performance of physical lithographic gates.
In the case of ASICs, there is an art to dynamic overclocking, and performance per chip is expected to vary significantly.
In the case of FPGAs, gate-level performance should be individually consistent, but is unknown and not taken into account when placing and routing components of a hardware design.

Sometimes, an FPGA programmer might manually specify how their logic should map to cells to achieve the tightest timing possible on, for example, high-speed I/O interfaces.
With fine-grained information of the chip quality across the fabric, hard-coded high-speed blocks could be placed to avoid "bad" cells and make the best use of "good" cells.
This requires a per-chip error profile that provides information across the spatial domain of the fabric.


## Background
The basic form of RTL logic is a series of registers separated by combinational logic.
Combinational logic is any type of boolean expression with an output that relies only on its current input.
Each register continuously outputs its stored value, and, when triggered to do so, updates ("latches") that value from its input.
Once a register latches a new value, its output changes to match, and those signals take time to propagate through combinational logic on the way to the next register.
There must be enough time for these signals to fully propagate before the next register latches its input.

The maximum frequency of latching (the clock speed) in a pipeline is the minimum of the frequencies of its combinational logic sections.
In other words, the combinational logic that takes the most time to propagate its inputs places an upper bound on the performance of the whole pipeline.

An FPGA (field-programmable gate array) is an array of logic "cells", each containing a look-up table (LUT) and a register, connected in configurable ways.
The look-up tables can implement any combinational logic, since the table can be programmed to be an AND gate, a multiplexer, etc.
It is the job of a place-and-route (PnR) tool to turn a list of circuit components into a 2D layout within the FPGA's cells.
This layout process takes as input a target clock speed, and tries to pack components together tightly enough that propagation delays are within the clock speed bounds.
After placing and routing the design, the tool then calculates the actual maximum clock speed of the layout it generated, based on some saved timing profile data (this is called static timing analysis).

Choosing a slow clock speed is an aggressive form of error prevention.
Knowing the performance and error profile of an FPGA would allow more advanced routing which unlocks further performance potential.
This performance doesn't come from nowhere: it comes from making fewer assumptions about delays, so that slower clocks and shorter interconnects are only applied where needed, instead of everywhere.

## Objectives
We propose an automated tool to determine the true timing behavior of each individual cell of a commercial FPGA.
The test setup would include a long chain of combinational logic, ending in a critical cell immediately before a register, with the clock speed set such that the clock tick arrives while the simulation claims that signals are still propagating through the critical cell.
By comparing expected and actual values latched in the final register, the tool would determine how the timing affects the error rate of that register, and the speed of the combinational logic before it.

Placing the critical path of combinational logic over different places on the chip would allow the final register to stay constant while exploring LUT delays.
Holding the critical path constant while changing the location of the final register (to a different neighbor of the final LUT) would let us explore register delay.
This setup would then be convolved over the whole FPGA fabric over many reprogramming and testing cycles, resulting in an empirical error profile for that particular chip.
Further work could incorporate these calibration results into an existing PnR algorithm.

## Feasibility and Impact
I already had a conversation with several members of the open-source FPGA community about the feasibility and usefulness of this project.
From that conversation, I learned that existing static timing analysis numbers were simply copied from the proprietary vendor tools.
There was also a simple benchmark project that a few members ran that demonstrated significant variations in LUT speed between chips *and between different placements on the same chip*, even though the individual elements had the same relative positions in all tests.

We discussed two uses for the timing data:
first, a human who would otherwise hard-code the placement of certain logic elements could test their own chip and "pin" their logic to a locally-optimal element.
Second, the open-source PnR tool (`nextpnr`) could read the empirical chip timing data for its final static analysis to give a more realistic maximum clock speed of the layout.
While `nextpnr` could in theory use the empirical data for routing, this would require significant modifications and more complicated algorithms.
That would be a task for future work.

The conversation also turned briefly to observing changes in performance at different temperatures and voltages.
Hopefully, my testing technique could simply be repeated at a different temperature and voltage, and the profiles could be interpolated to learn a more complete performance and error profile for each element.
This type of analysis could lead to automated PnR output reports such as "you can undervolt this layout to 0.95V while retaining 99.99% accuracy", or "this layout is only expected to operate between 20°C and 80°C."
Such messages would need to be worded carefully to avoid legal issues if someone damages their FPGA, but the suggestions could remain within the manufacturer's stated safe operating range.

## Development Timeline
| Week | Goal                                                 |
|:----:|------------------------------------------------------|
|   4  | FPGA toolchain installed, tested, and functional     |
|   5  | Design theoretical on-fabric testing construction    |
|   6  | Observe any changes in error rate that depend on PnR |
|   7  | Feb. 15: Mid-report report due                       |
|   8  | Automated convolution done and data acquired         |
|   9  | Data analyzed, paper draft done                      |
|  10  | Mar. 8-10: Final presentation                        |
|  11  | Mar. 15: Final paper                                 |

