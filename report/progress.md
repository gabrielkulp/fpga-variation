# Mid-Term Progress Report
Gabriel Kulp, Matthew Phillips

## Updates
We now have a better idea of the project space we're working in.
For example, there are several approaches to designing an on-fabric fixture that are error-sensitive, and these different approaches are capable of measuring different tolerances.
Broadly, we can try to ride the edge of timing violations in synchronous logic, or make a loop of combinational logic and measure its speed.
The latter is looking more standard and promising.

We've also come across more community discussion of error tolerances in FPGA place-and-route (PnR).
This included anecdotal reports that the maximum clock speed reported by the existing PnR tool can be increased around 50% without introducing errors.
In this same discussion we learned that the timing data for the open-source PnR tool was extracted from the proprietary toolchain, and is therefore provided by the manufacturer, rather than any empirical testing.

Additionally, we found a few papers on the topic of FPGA variance.
This is execellent because it suggests we can find meaningful results, provides citations for our final paper, and provides suggestions for measurement and analysis methods. 

## Looking Forward
We have decided on an inital approach to on-fabric testing: an oscillator.
This is just a loop of NOT gates, with one also connected to a counter.
Then with another counter we can compare the number of oscillations per clock period, and compare this number as we change parameters of the oscillator.
Notably, PnR has a "pre-place" option which lets us pin the oscillator to one spot and route the rest of the logic around it.
Finally, we already have a functional serial interface through which we can communicate oscillator timings back to the host computer for logging.
Putting these together, we can observe the speed of an oscillator at each position on the FPGA fabric. 

We hope to use the our gateware across two development boards from different manufacturers.
Though the FPGA chips are identical, these two manufacturers are more likely to have received different batches than if we had two boards from the same manufacturer.
We expect to see timing variation between the chips to a higher degree than the variation on the same chip.

Scripting the PnR pre-place option looks possible and promising, meaning we could have a unified piece of software that repeatedly flashes the FPGA and collects statistics.
We can then share this tool with the FPGA community and could collect statistics across many more chips.

## Timeline
Our inital progress has not advanced in line with original projections.
We have had trouble finding finding time between coursework from other classes to meet and work together, but as the project progresses, we have more parallel tasks available.
We're hopeful 

The overall project outlook is positive.
We have updated our timeline below.

| Week | Goal                                               |
|:----:|----------------------------------------------------|
|   4  | FPGA toolchain installed, tested, and functional   |
|   5  | Design space research, design on-fabric instrument |
|   6  | Set up toolchain, git repo, etc.                   |
|   7  | Feb. 15: Mid-report report due                     |
|   8  | Finish testing software and gateware, gather data  |
|   9  | Paper draft, organize and visualize data           |
|  10  | Mar. 8-10: Final presentation                      |
|  11  | Mar. 15: Final paper                               |

