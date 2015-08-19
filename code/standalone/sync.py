#Description: This code hunts a IQ sample file for a given PN sequence.
#Notes: Keep in mind that the threshold may need to be adjusted for your setup.

import numpy
import struct
import os
import sys
import json
import matplotlib.pyplot as plt

from progressbar import ProgressBar, Percentage, Bar

pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()

########## Global Constants ##########

#4 bytes == 32 bits
FLOATSIZE = 4

#Values come in interleaved as a complex number (pair of floats)
COMPLEX_SIZE = FLOATSIZE * 2



########## Functions ##########

#Scale a PN to make it effectively larger.
def resizePN(pn_list, resize_factor):

	resized_pn = []

	for chip in pn_list:
		for i in range(0, resize_factor):
			resized_pn.append(chip)

	return resized_pn


def convertToFloat(data_chunk, corr_buffer_real, corr_buffer_imag):

	#iterate over how many complex samples we have and store them in the compare buffer.
	for j in range(0, len(data_chunk)/COMPLEX_SIZE ):

		#as we iterate over the data, pull new pieces for processing each time.
		realpart = data_chunk[ j*8 : j*8 + 4 ]
		imagpart = data_chunk[ j*8 + 4 : j*8 + 8]

		#convert the raw data to floating point vaules
		realpart = struct.unpack('@f', realpart)[0]
		imagpart = struct.unpack('@f', imagpart)[0]

		#add the newly converted values to the correlation buffer for use
		corr_buffer_real.append(realpart)
		corr_buffer_imag.append(imagpart)

	return (corr_buffer_real, corr_buffer_imag)


#TODO: Simply this
def progress(position, file_size):

	percent_done = (float(position) / float(file_size)) * 100
	pbar.update(percent_done)

	return percent_done


def correlate(pn_sequence, corr_buffer):

	pn_resized_length = len(pn_sequence)

	#The compare buffer should now be full. Compare the pn_sequence against the data buffer.
	correlation_normal = numpy.correlate(pn_sequence, corr_buffer)[0]	#normal

	return correlation_normal


def magnitude(a, b):

	#calculate the magnitude
	a = numpy.power(a, 2)
	b = numpy.power(b, 2)

	mag = numpy.add(a, b)

	#We really don't need to take the square root here.  It just adds overhead
	#and we may get higher resolution on the threshold without doing it. Threshold
	#just needs to be adjusted accordingly (make it larger by a square.)
	
	#mag = numpy.sqrt(mag)

	return mag



def checkForPeak(correlation_before, correlation_normal, correlation_after):

	peak = None

	#Check if the peak is above a threshold and is the highest point between the two adjacent 
	if (abs(correlation_after) < abs(correlation_normal)) and \
	   (abs(correlation_before) < abs(correlation_normal)):

	   #if there is, return True
	   return True

	else:
		#if not, return false
		return False



def plotData(peaks, correlation_data_real, correlation_data_imag):
	plt.plot(peaks, 'ro')
	#plt.plot( numpy.absolute(correlation_data_real) )
	#plt.plot( numpy.absolute(correlation_data_imag) )
	plt.plot( correlation_data_real )
	plt.plot( correlation_data_imag )
	plt.show()



def sync(file_descriptor, file_size, seek_position, pn, threshold, output_file):

	result = file_descriptor.seek(seek_position)

	#Initialize variables for use in correlation loop

	#lists to hold the final processed data
	correlation_data_real = []
	correlation_data_imag = []
	correlation_data_magnitude = []

	#Buffers to hold data to correlate against. Will be the length of the expanded PN sequence.
	corr_buffer_real = []
	corr_buffer_imag = []


	while True:

		#Get our progress so far.
		our_progress = progress( file_descriptor.tell(), file_size)
		if our_progress > 97:
			break

		#Holds the data read from the file
		data_chunk = None


		#if the correlation buffer needs data. Use the length of compare_buffer_real since it should be the same as compare_buffer_imag at all times
		#Load an extra two samples for early/late detection.
		if len(corr_buffer_real) < (len(pn) + 2):

			#calculate how many samples to read
			samples_to_read = (len(pn) + 2) - len(corr_buffer_real)

			#translate samples to bytes
			bytes_to_read = samples_to_read * COMPLEX_SIZE

			#read from the data file
			data_chunk = file_descriptor.read(bytes_to_read)

			#convert to float
			convertToFloat(data_chunk, corr_buffer_real, corr_buffer_imag)


		#correlate the pn and the buffer.  Shift one sample over so we have room for early and late detection.
		correlation_real_normal = correlate(pn, corr_buffer_real[1 : len(corr_buffer_real)-1 ])
		correlation_imag_normal = correlate(pn, corr_buffer_imag[1 : len(corr_buffer_imag)-1 ])


		correlation_magnitude_normal = magnitude(correlation_real_normal, correlation_imag_normal)

		correlation_data_magnitude.append(correlation_magnitude_normal)

		#keep track of the correlations so far.
		#correlation_data_real.append(correlation_real_normal)
		#correlation_data_imag.append(correlation_imag_normal)


		#Check the correlation against the threshold (see if we correlate)
		#if (correlation_real_normal >= threshold) or (correlation_real_normal <= -threshold):
		if (correlation_magnitude_normal >= threshold) or (correlation_magnitude_normal <= -threshold):

			#correlate the pn and the buffer.  Shift so we have room for early and late detection.
			correlation_real_before = correlate(pn, corr_buffer_real[0 : len(corr_buffer_real)-2 ])
			correlation_real_after = correlate(pn, corr_buffer_real[2 : len(corr_buffer_real) ])

			correlation_imag_before = correlate(pn, corr_buffer_imag[0 : len(corr_buffer_imag)-2 ])
			correlation_imag_after = correlate(pn, corr_buffer_imag[2 : len(corr_buffer_imag) ])

			correlation_magnitude_before = magnitude(correlation_real_before, correlation_imag_before)
			correlation_magnitude_after = magnitude(correlation_real_after, correlation_imag_after)

			#check for a peak
			#result = checkForPeak(correlation_real_before, correlation_real_normal, correlation_real_after)
			result = checkForPeak(correlation_magnitude_before, correlation_magnitude_normal, correlation_magnitude_after)



			#if there is a peak, return it's position
			if result:

				#write out the file
				corr_buffer_real_despread = numpy.multiply(pn, corr_buffer_real[1 : len(corr_buffer_real)-1 ])
				corr_buffer_imag_despread = numpy.multiply(pn, corr_buffer_imag[1 : len(corr_buffer_imag)-1 ])


				for j in range(0, len(corr_buffer_real_despread) ):
					real_data_write = struct.pack('@f', corr_buffer_real_despread[j])
					output_file.write(real_data_write)
					imag_data_write = struct.pack('@f', corr_buffer_imag_despread[j])
					output_file.write(imag_data_write)
				

				#calculate the position of the correlation
				position = file_descriptor.tell() - ( len(pn) * COMPLEX_SIZE )
				return ( position , correlation_magnitude_normal)

		#Remove the first element of each buffer so we can load one more to process the next sample in time
		corr_buffer_real.pop(0)
		corr_buffer_imag.pop(0)




def loadFile(file_path):
	#load the signal capture
	file_descriptor = open(file_path, "rb")

	#get the signal capture's fie properties
	file_size = os.path.getsize(file_path)

	print "File Size:", str(file_size)
	print "Number of complex samples:", str(file_size/COMPLEX_SIZE)

	return (file_descriptor, file_size)


#we may need to add padding to a file to get gnuradio to dump the decoded psk correctly.
def padFile(output_file):
	for i in range(0, COMPLEX_SIZE * 100000):
		real_data_write = struct.pack('@f', 0)
		output_file.write(real_data_write)
		imag_data_write = struct.pack('@f', 0)
		output_file.write(imag_data_write)




#Initial inputs
pn = [1, 1, 1, 1, 1, 1, 1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, 1, 1, -1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, 1, 1, -1, -1, -1, 1, -1, -1, -1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, 1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, 1, -1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, 1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, 1, 1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, -1, -1]
pn_scale = 4
file_path = "/Users/colby/globalstar/workingdir/raw_capture_converted_5m.iq"
output_file_path = "/Users/colby/globalstar/workingdir/despread.iq"
threshold = 1000
seek_position = 0
chip_rate = 1250000
sample_rate = 5000000
pn_sequences_per_bit = 49

#calculate how much we need to scale the PN code
pn_scale = sample_rate / chip_rate

#scale the pn sequence to match the sample rate of the data
pn = resizePN(pn, pn_scale)

#load the sample file
(file_descriptor, file_size) = loadFile(file_path)

#load the output file
newfile = open(output_file_path, 'wb')

#pad the output file with 0's.  This helps when feeding the data into a PSK
#decoder.  Without the padding, it appears that not all of the data leaves the
#buffer.
padFile(newfile)

graph_data = []

while True:

	try:
		#find the first correlation
		print "Searching for correlation at position:", str(seek_position)
		(sync_position, correlation) = sync(file_descriptor, file_size, seek_position, pn, threshold, newfile)
		graph_data.append(correlation)

		print "Found correlation at:", str(sync_position)

		#search for the next correlation
		seek_position = sync_position + ( ( len(pn) * COMPLEX_SIZE ) - 4 * COMPLEX_SIZE )

	except Exception as e:
		print e
		break


#pad the end of the output file
padFile(newfile)

plt.plot(graph_data)
plt.show()

print "Done."


