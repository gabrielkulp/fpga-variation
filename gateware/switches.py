from amaranth import *
from amaranth.build import *

switches_resource =	Resource(
	"switches", 0,
	PinsN("1 2 3 4 7 8 9 10", dir='i', conn=("pmod",1)),
	Attrs(IO_STANDARD="SB_LVCMOS33", PULLUP=1)
)

class Switches(Elaboratable):
	def __init__(self):
		self.value = Signal(8)
	
	def elaborate(self, platform):
		switches = platform.request("switches")
		m = Module()
		m.d.comb += self.value.eq(~switches[::-1])
		return m
