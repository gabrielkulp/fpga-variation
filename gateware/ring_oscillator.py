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

		buffers_in  = Signal(self.length)
		buffers_out = Signal(self.length)
		
		# make main loop
		for buf_in, buf_out, i in zip(buffers_in, buffers_out, range(self.length)):
			inverter = Instance(
				"SB_LUT4",
				a_BEL        = f"X{self.x}/Y{self.y}/lc{i}",
				a_DONT_TOUCH = "TRUE",
				p_LUT_INIT   = 0b01, # NOT gate
				i_I0         = buf_in,
				i_I1         = Const(0),
				i_I2         = Const(0),
				i_I3         = Const(0),
				o_O          = buf_out
			)
			m.submodules += inverter
		# connect ends of loop together
		m.d.comb += buffers_in.eq(Cat(buffers_out[-1], buffers_out[0:-1]))

		# drive this clock domain with the output of the loop
		m.d.comb += ClockSignal("loop").eq(buffers_out[-1])

		reset_mask = Repl(~self.reset, self.width)

		m.d.loop += self.counter.eq((self.counter + self.enable) & reset_mask)

		return m
