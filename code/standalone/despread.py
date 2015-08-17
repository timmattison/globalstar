#Description: This code will despread a file containing bytes of value 0x01
#and 0x00 assuming one sample per symbol. Notes: Preamble for data =
#0000001011, the PN code should repeat 49 times for each true bit of data.

import sys
import binascii

PN = '000000001101001010010001010101000110110010010110011001011100010010011101110110000101101101111000011101011000111000001010000110001011110101001101011101001111100110111001111001000000100011110111110110101011010000011111100011001110010101111111010001000010011'

pn_per_bit = 49
bits_per_packet = 144
pn_len = len(PN)


#XORs 255 bits of data fed to it and averages all those bits to hopefully reduce errors
def xorAVG(data):
	average = 0

	for i in range(0, pn_len):
		dataBit = ord(data[i])
		pnBit = int(PN[i])

		xorData = dataBit ^ pnBit
		average += xorData

	return int( round( float(average) / pn_len ) )




if len(sys.argv) > 1:
	path = sys.argv[1]
else:
	print "Error: No path given."
	sys.exit()


f = open(path, "rb")


signal49 = []
for i in range(0, pn_per_bit * bits_per_packet):

	data = f.read(pn_len)
	avg = xorAVG(data)
	signal49.append(avg)


numDataSets = len(signal49)/pn_per_bit

for i in range(0, numDataSets):
	average = 0

	for i in range(0, pn_per_bit):
		average += signal49.pop(0)

	sys.stdout.write(str(average/pn_per_bit))

print ""
