#!/usr/bin/env python3

from amaranth_boards.icebreaker import ICEBreakerPlatform
from amaranth_boards.test.blinky import Blinky

board = ICEBreakerPlatform()
board.add_resources(board.break_off_pmod)

try:
	board.build(Blinky(), do_program=True)
except Exception as e:
	print(str(e))

