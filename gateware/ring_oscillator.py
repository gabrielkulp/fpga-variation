#!/usr/bin/env python3

"""
https://github.com/amaranth-lang/amaranth/issues/122
https://github.com/TrustedThings/litepuf
https://github.com/amaranth-lang/amaranth-boards/blob/main/amaranth_boards/icebreaker.py
"""

from amaranth import *
from amaranth_boards.icebreaker import *
from amaranth.lib.cdc import FFSynchronizer

#class ring_oscillator(Elaboratable):
#	def __init__(self, length, width):
#		self.ctr = Signal(width, reset=0)
#
#		self.length = length
#		self.ring = [ Signal() ]*length
#
#	def elaborate(self, platform):
#		led = platform.request("led", 0)
#
#		m = Module()
#		m.d.comb += self.ring[-1].eq(~self.ring[0])
#		for i in range(self.length - 1):
#			m.d.comb += self.ring[i].eq(~self.ring[i+1])

class Ring_Oscillator(Elaboratable):
	def __init__(self, length, width, x, y):
		if length > 7:
			raise IndexError("iCE40 only has 8 lc per BEL")
		if x < 1 or x > 24:
			raise IndexError("X must be 1-24")
		if y < 1 or y > 30:
			raise IndexError("Y must be 1-30")
		self.length   = length
		self.width    = width
		self.x        = x
		self.y        = y
		self.counter  = Signal(width)
		self.enable   = Signal()
		self.reset    = Signal()

	def elaborate(self, platform):
		m = Module()

		cd_loop = ClockDomain("loop", async_reset=True, local=True)
		m.domains.loop = cd_loop

		ring_in  = Signal(self.length)
		ring_out = Signal(self.length)

		# make main loop
		for buf_in, buf_out, i in zip(ring_in, ring_out, range(self.length)):
			inverter = Instance(
				"SB_LUT4",
				a_BEL        = f"X{self.x}/Y{self.y}/lc{i}",
				a_DONT_TOUCH = True,
				a_BLACKBOX   = True,
				p_LUT_INIT   = Const(0b01), # NOT gate
				i_I0 = buf_in,
				i_I1 = Const(0),
				i_I2 = Const(0),
				i_I3 = Const(0),
				o_O  = buf_out
			)
			m.submodules += inverter
		
#		m.d.comb += ring_in[0].eq(ring_out[-1] & ~self.reset)
		out_sig = Signal()
		m.d.comb += ring_in[0].eq(out_sig)
		starter = Instance("SB_LUT4",
			a_BEL        = f"X{self.x}/Y{self.y}/lc7",
			a_DONT_TOUCH = True,
			a_BLACKBOX   = True,
			p_LUT_INIT   = Const(0b1000,4), # AND gate
			i_I0 = ring_out[-1],
			i_I1 = ~self.reset,
			i_I2 = Const(0),
			i_I3 = Const(0),
			o_O  = out_sig)
		m.submodules += starter


		# connect ends of loop together
		m.d.comb += ring_in.bit_select(1,self.length-1).eq(ring_out[0:-1])
#		m.d.comb += ring_in.eq(Cat(ring_out[-1], ring_out[0:-1]))

		# drive this clock domain with the output of the loop
		m.d.comb += ClockSignal("loop").eq(ring_out[-1])

		reset_mask = Repl(~self.reset, self.width)
		m.d.loop += self.counter.eq((self.counter + self.enable) & reset_mask)

		return m
