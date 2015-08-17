#Description: This code takes a string input of a valid packet and spreads it
#using the Globalstar PN code. This data can then be fed into a BPSK modulator
#to transmit spread data. Sample packet: 0000001011001010011011000111101000001
#11000000000011000000000000000000000000000000000000000000000000000000000000100
#000000011100010100111010101001


import sys



def spread(packet):

	outputfilename = "spread.bytes"
	pn_code = "000000001101001010010001010101000110110010010110011001011100010010011101110110000101101101111000011101011000111000001010000110001011110101001101011101001111100110111001111001000000100011110111110110101011010000011111100011001110010101111111010001000010011"
	chips_seqs_per_symbol = 49


	#Generate spread data
	encoded = []

	for bit in packet:
		for i in range(0, 49):
			for pn_bit in pn_code:

				xored = int(bit) ^ int(pn_bit)
				encoded.append( xored )
				#sys.stdout.write( str( xored ) )



	data_bytes = bytearray(int(i) for i in encoded)

	print "Data Length:", str( len(data_bytes) )

	with open(outputfilename, 'wb') as output:
		output.write(data_bytes)

	print "Done"





if len(sys.argv) > 1:
    packet = sys.argv[1]
else:
    print "Error: No data given."
    sys.exit()


spread(packet)

