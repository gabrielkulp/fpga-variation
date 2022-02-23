#!/usr/bin/env python3

from amaranth import *
from amaranth_boards.icebreaker import ICEBreakerPlatform

from ring_oscillator import ring_oscillator

board = ICEBreakerPlatform()
try:
	board.build(ring_oscillator(7,26), do_program=True,
		nextpnr_opts="--ignore-loops --timing-allow-fail")
except Exception as e:
	print(str(e))
