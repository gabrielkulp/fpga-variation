#!/usr/bin/env python
import gateware

if  __name__ == "__main__":
	all_coords = []
	for x in range(1,25): # 1-24
		for y in range(1,31): # 1-30
			all_coords.append((x,y))
	
	with open("results.json", "w") as f:
		f.write("{\n")
		for coords, i in zip(all_coords, range(len(all_coords))):
			key = " ".join(map(str, coords))
			results = gateware.run(coords)
			f.write(f"\t\"{key}\": [")
			f.write(", ".join(map(str, results)))
			if i == len(all_coords)-1:
				f.write("]\n")
			else:
				f.write("],\n")
			f.flush()
		f.write("}\n")
