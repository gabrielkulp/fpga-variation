#!/usr/bin/env python3

import json

bel_list=[]
used_bels=[]

#get belIDs put them in a useful container
try:
	with open("bel_list", "r") as fp:
		bel_list = json.load(fp)
	with open("used_bels", "r") as fp:
		used_bels = json.load(fp)
except Exception as e:
	bels=ctx.getBels()
	for b in bels:
		bel_list.append(b)

#bind bels to cells
for n,c in ctx.cells:
	for b in bel_list:
		#check if bel and cell types are valid, only place the most common type
		if c.type == 'ICESTORM_LC' and c.type == ctx.getBelType(b):
			ctx.bindBel(b, c, STRENGTH_USER)
			used_bels.append(b)
			bel_list.remove(b)
			break

#save progress for next iteration
with open("bel_list", "w") as fp:
	json.dump(bel_list, fp)
with open("used_bels", "w") as fp:
	json.dump(bel_list, fp)
  