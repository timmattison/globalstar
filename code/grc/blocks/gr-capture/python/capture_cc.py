#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
import time
from gnuradio import gr



threshold = .0005
rms_toggle = 0

samples_per_symbol = 4
samples_per_pn = 255
pn_per_bit = 49
bits_per_packet = 144
extra_bit = 50000  #we need a little extra info to get the last bit
extra = 10000       #to hold any overage from the buffer

#How many samples do we need to write out
packet_size = (samples_per_symbol * samples_per_pn * pn_per_bit * bits_per_packet) + extra_bit
sample_count = 0


packet_data = numpy.ndarray(shape=(packet_size + extra), dtype=numpy.complex64)



class capture_cc(gr.sync_block):
    """
    docstring for block capture_cc
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="capture_cc",
            #in_sig=[<+numpy.float+>],
            in_sig=[numpy.complex64, numpy.float32],
            out_sig=None)


    def work(self, input_items, output_items):
        in0 = input_items[0]
        # <+signal processing here+>

        #input_items[0] = complex
        #input_items[1] = rms

        global rms_toggle
        global sample_count


        #print input_items[1][0]
        #print type(input_items[0])

        #if the first element meets the threshold (I know, its a shortcut), the start logging
        if input_items[1][0] > threshold:
            rms_toggle = 1

        if rms_toggle == 1 and sample_count < packet_size:

            packet_data[ sample_count : sample_count+len(input_items[0]) ] = input_items[0][ 0:len(input_items[0]) ]

            sample_count += len(input_items[0])


            print sample_count

        elif sample_count > packet_size:
            packet_data.tofile('/Users/colby/globalstar/workingdir/raw_capture_4m-' + str( int(time.time()) ) + '.iq')
            print "Done"
            rms_toggle = 0
            sample_count = 0



        return len(input_items[0])

