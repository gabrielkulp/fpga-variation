#!/usr/bin/env python3

from amaranth import *
from amaranth_boards.icebreaker import *

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

class ring_oscillator(Elaboratable):
	def __init__(self, length, width):
		self.length  = length
		self.width   = width

	def elaborate(self, platform):
		user_led = platform.request("led_r", 0)

		m = Module()

		cd_chain = ClockDomain(async_reset=True)#, reset_less=True)
		m.domains.chain = cd_chain

		buffers_in  = Signal(self.length)
		buffers_out = Signal(self.length)
		
		m.d.comb += buffers_in.eq(Cat(buffers_out[-1:], buffers_out[0:-1]))
		
		for buf_in, buf_out in zip(buffers_in, buffers_out):
			inverter = Instance(
				"SB_LUT4",
				p_LUT_INIT = 0b01, # NOT gate
				i_I0       = buf_in,
				i_I1       = Const(0),
				i_I2       = Const(0),
				i_I3       = Const(0),
				o_O        = buf_out
			)
			m.submodules += inverter

		m.d.comb += cd_chain.clk.eq(buffers_out[-1])

		counter    = Signal(self.width)
		m.d.chain += counter.eq(counter + 1)
		m.d.comb  += user_led.o.eq(counter[-1])

		return m
