#!/usr/bin/env python3

import serial
from time import sleep

from amaranth import *
from amaranth_boards.icebreaker import ICEBreakerPlatform

from . import UART
from . import Ring_Oscillator
from . import Seven_seg, seven_seg_resource
from . import Switches,  switches_resource

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
	def __init__(self, x, y, cycle_count):
		self.x = x
		self.y = y
		self.cycle_count = cycle_count
		self.uart = None
		self.ring = Ring_Oscillator(7, 8, self.x, self.y)
		self.byte_out = Seven_seg()

	def elaborate(self, platform):
		m = Module()
		m.submodules += [self.ring, self.byte_out]

		uart_pins = platform.request("uart")
		self.uart = UART(uart_pins, clk_freq=12000000, baud_rate=baud)
		m.submodules += self.uart
		
		read_state = Signal(8, reset=20+self.cycle_count)

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
		# send back the oscillator count
		with m.If(rx_strobe):
			m.d.sync += [
				#self.data.eq(self.uart.rx_data), # data in from UART
				self.byte_out.value.eq(data),
				#data.eq(self.ring.),
				empty.eq(0),
			]
			with m.If(read_state == 0):
				# start countdown to next measurement
				m.d.sync += read_state.eq(20+self.cycle_count)
		with m.If(tx_strobe):
			m.d.sync += empty.eq(1)


		with m.If(read_state != 0):
			m.d.sync += read_state.eq(read_state - 1)

		with m.Switch(read_state):
			with m.Case(20+self.cycle_count):
				m.d.sync += self.ring.reset.eq(0) # enable
			with m.Case(10+self.cycle_count):
				m.d.sync += self.ring.enable.eq(1) # start counting
			with m.Case(10):
				m.d.sync += self.ring.enable.eq(0) # stop counting
			with m.Case(1):
				m.d.sync += data.eq(self.ring.counter) # copy value
			with m.Case(0):
				m.d.sync += self.ring.reset.eq(1) # reset counter
		return m


def _flash(coords, cycle_count):
	x,y = coords
	board = ICEBreakerPlatform()
	board.add_resources([seven_seg_resource, switches_resource])
	board.build(Top(x, y, cycle_count), do_program=True,
		nextpnr_opts="--ignore-loops --timing-allow-fail")

def run(coords, cycle_count=64, sample_count=100, sample_rate=100, flash=True, verbose=False):
	if flash:
		_flash(coords, cycle_count)
		sleep(1)

	ser = serial.Serial('/dev/ttyUSB1', 115200)

	# discard first read
	ser.write(b'0')
	ser.read(1)
	sleep(1.0/sample_rate)

	records = []
	for _ in range(sample_count):
		ser.write(b'0') # trigger measurement
		new_val = ord(ser.read(1))/cycle_count
		records.append(new_val)
		print(new_val, end=", ", flush=True) if verbose else ()
		sleep(1.0/sample_rate)

	print() if verbose else ()
	print(f"At {coords} the average is", round(sum(records)/len(records), 2))
	return records
