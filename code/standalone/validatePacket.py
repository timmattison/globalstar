#Description: This code takes command line argument as a string of bits representing a Globalstar simplex data network packet. It decodes the packet and verifies it's CRC.

#Packet Format

# 0000001011 00101001101100011110100000 0101 0000 0000 010011110000000100000010000010000000000000000100000000000000000000000000 000011001000001010010011
#  PREAMBLE            STU ID           MSG# PKT# SEQ#                                  USER INFO										CRC24					   


import sys


#Pass a string of binary (including preamble and CRC)
def validate(binaryPacket):

	if 144 != len(binaryPacket):
		print "Error: Invalid Packet Length"
		sys.exit(0)

	preamble = binaryPacket[0:10]
	stuID = binaryPacket[10:36]
	msgNum = binaryPacket[36:40]
	pktNum = binaryPacket[40:44]
	seqNum = binaryPacket[44:48]
	userData = binaryPacket[48:120]
	crc24 = binaryPacket[120:144]

	checkPreamble(preamble)
	crcTwentyfour(binaryPacket)

	print "Manufacturer:", str( int(stuID[0:3], 2) )
	print "Unit ID:", str( int(stuID[3:26], 2) )
	print "Message Number:", str( int(msgNum, 2) )
	print "Packet Number:", str( int(pktNum, 2) )
	print "Sequence Number:", str( int(seqNum, 2) )
	print "UserData:", str( hex(int(userData, 2)) )


def checkPreamble(preamble):

	if '0000001011' != preamble:
		print "Warning: Invalid Preamble.  Data may still be intact, checking CRC."


def crcTwentyfour(TX_Data):

    k = 0
    m = 0

    TempCRC = 0
    Crc = 0xFFFFFF
    
    for k in range(0,14):  #calc checksum on 14 bytes starting with esn

    	TempCRC = int(TX_Data[ (k*8)+8 : (k*8)+8+8 ], 2)   #offset to skip part of the preamble (dictated by algorithm)

    	if 0 == k:
    		TempCRC = TempCRC & 0x3f #skip 2 preamble bits in byte0
		

    	Crc = Crc ^ (TempCRC)<<16


    	for m in range(0,8):
    		Crc = Crc << 1

    		if Crc & 0x1000000:
    			Crc = Crc ^ 0114377431L #seed CRC


    Crc = (~Crc) & 0xffffff;
    #end crc generation. lowest 24 bits of the long hold the CRC


    byte14 = (Crc & 0x00ff0000) >> 16 #first CRC byte to TX_Data
    byte15 = (Crc & 0x0000ff00) >> 8 #second CRC byte to TX_Data
    byte16 = (Crc & 0x000000ff) #third CRC byte to TX_Data

    final_crc = (byte14 << 16) | (byte15 << 8) | byte16

    if final_crc != int(TX_Data[120:144], 2):
    	print "Error: CRC failed"
    	sys.exit(0)


if len(sys.argv) > 1:
    packet = sys.argv[1]
else:
    print "Error: No data given."
    sys.exit()


validate(packet)