from amaranth import *
from amaranth.build import *

# add this with platform.add_resources
seven_seg_resource = Resource(
	"seven_seg", 0,
	Subsignal("segments", PinsN("1 2 3 4 7 8 9", dir="o", conn=("pmod",0)), Attrs(IO_STANDARD="SB_LVCMOS")),
	Subsignal("digit_sel", PinsN("10", dir="o", conn=("pmod",0)), Attrs(IO_STANDARD="SB_LVCMOS33")),
)

# (private) one-digit decoder
class _Digit_to_segments(Elaboratable):
	def __init__(self):
		self.digit    = Signal(4) # input
		self.segments = Signal(7) # output
	
	def elaborate(self, _platform):
		m = Module()
		with m.Switch(self.digit):
			for (n,   seg_val) in [
				(0x0, 0b0111111),
				(0x1, 0b0000110),
				(0x2, 0b1011011),
				(0x3, 0b1001111),
				(0x4, 0b1100110),
				(0x5, 0b1101101),
				(0x6, 0b1111101),
				(0x7, 0b0000111),
				(0x8, 0b1111111),
				(0x9, 0b1101111),
				(0xA, 0b1110111),
				(0xB, 0b1111100),
				(0xC, 0b0111001),
				(0xD, 0b1011110),
				(0xE, 0b1111001),
				(0xF, 0b1110001)]:
				with m.Case(n):
					m.d.sync += self.segments.eq(seg_val)
		return m

class Seven_seg(Elaboratable):
	def __init__(self):
		self.value = Signal(8) # input
		self.low_decoder  = _Digit_to_segments()
		self.high_decoder = _Digit_to_segments()

	def elaborate(self, platform):
		seven_seg = platform.request("seven_seg")
		m = Module()

		m.submodules += self.low_decoder
		m.submodules += self.high_decoder

		counter = Signal(11)
		display_state = counter[-3:]

		m.d.comb += [
			self.low_decoder.digit.eq(self.value[:4]),
			self.high_decoder.digit.eq(self.value[4:])
		]

		# 25% duty cycle
		m.d.sync += counter.eq(counter + 1)
		with m.Switch(display_state):
			with m.Case("00-"):
				m.d.sync += seven_seg.segments.eq(self.low_decoder.segments)
			with m.Case("010"):
				m.d.sync += seven_seg.segments.eq(0) # turn off digit
			with m.Case("011"):
				m.d.sync += seven_seg.digit_sel.eq(1) # switch to high digit
			with m.Case("10-"):
				m.d.sync += seven_seg.segments.eq(self.high_decoder.segments)
			with m.Case("110"):
				m.d.sync += seven_seg.segments.eq(0) # turn off digit
			with m.Case("111"):
				m.d.sync += seven_seg.digit_sel.eq(0) # switch to low digit
		return m
