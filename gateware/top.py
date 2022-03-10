#!/usr/bin/env python3

from amaranth import *
from amaranth_boards.icebreaker import ICEBreakerPlatform

import serial
from time import sleep

from uart import UART
from ring_oscillator import Ring_Oscillator
from seven_seg import Seven_seg, seven_seg_resource
from switches  import Switches,  switches_resource

baud = 115200

class Serial_Top(Elaboratable):
	def __init__(self):
		self.byte_in = Switches()
		self.byte_out = Seven_seg()
		self.uart = None

	def elaborate(self, platform):
		m = Module()
		m.submodules += [self.byte_in, self.byte_out]
		
		uart_pins = platform.request("uart")
		self.uart = UART(uart_pins, clk_freq=12000000, baud_rate=baud)
		m.submodules += self.uart

		# auto-reply with data immediately
		data = Signal(8)
		rx_strobe = Signal()
		tx_strobe = Signal()
		empty = Signal(reset=1)
		# auto-reply with `data` I think?
		m.d.comb += [
			rx_strobe.eq(self.uart.rx_ready & empty),
			tx_strobe.eq(self.uart.tx_ack & ~empty),
			self.uart.rx_ack.eq(rx_strobe),
			self.uart.tx_data.eq(data),
			self.uart.tx_ready.eq(tx_strobe)
		]

		# handle setting local values
		counter = Signal(24)
		disp = Signal(8)
		m.d.comb += self.byte_out.value.eq(disp)
		with m.If(counter == 0):
			m.d.sync += disp.eq(disp + self.byte_in.value)
			m.d.sync += counter.eq(12000000)
		with m.Else():
			m.d.sync += counter.eq(counter - 1)

		# send back the accumulator
		with m.If(rx_strobe):
			m.d.sync += [
				#self.data.eq(self.uart.rx_data),
				data.eq(disp),
				empty.eq(0)
			]
		with m.If(tx_strobe):
			m.d.sync += empty.eq(1)

		return m

class Top(Elaboratable):
	def __init__(self):
		#self.uart = None
		self.ring = Ring_Oscillator(5, 8)
		self.byte_out = Seven_seg()
	def elaborate(self, platform):
		m = Module()
		m.submodules += [self.byte_out, self.ring]

		#uart_pins = platform.request("uart")
		#self.uart = UART(uart_pins, clk_freq=12000000, baud_rate=baud)
		#m.submodules += self.uart
		
		counter = Signal(24)
		disp = Signal(8)
		m.d.comb += self.byte_out.value.eq(disp)

		user_led = platform.request("led_r", 0)
		with m.If(counter == 0):
			m.d.sync += counter.eq(12000000)
		with m.Else():
			m.d.sync += counter.eq(counter - 1)

		with m.Switch(counter):
			with m.Case(300):
				m.d.sync += disp.eq(self.ring.counter[:8]) # read counter
				m.d.sync += user_led.o.eq(1)
			with m.Case(200):
				m.d.sync += self.ring.reset.eq(1) # reset counter
			with m.Case(100):
				m.d.sync += self.ring.reset.eq(0)
				m.d.sync += user_led.o.eq(0)
			with m.Case(8):
				m.d.sync += self.ring.enable.eq(1) # start counting
			with m.Case(0):
				m.d.sync += self.ring.enable.eq(0) # stop counting
		
		return m


board = ICEBreakerPlatform()
board.add_resources([seven_seg_resource, switches_resource])
board.build(Top(), do_program=True,
	nextpnr_opts="--ignore-loops --timing-allow-fail")
