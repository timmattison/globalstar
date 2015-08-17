code/
-----
The "code" Contains two folders, "grc" and "standalone".  GRC contains gnuradio-companion flowgraphs and standalone contains standalone code used to process raw IQ files.

Many of the flow graphs depend on previously recorded data, or various input files.  These files can be downloaded as the "data" folder from:

https://www.dropbox.com/sh/kzfx4lf35ooytyw/AABwq3QsylrBNIB8cBlIFFuZa?dl=0

The "data" folder contains two folders, "bytes" and "iq".  IQ contains raw IQ sampling data from GNURADIO and bytes contains various binary files.  These files represent binary sequences as bytes, with 0x01 representing 1 and 0x00 representing 0.  These files are used to hold various packet data or received/decoded data.



----------------
code/standalone/
----------------

despread.py
-----------
Description: See description inside.
Usage: Provide the program with a byte file where each byte (0x01 or 0x00) represents a binary BPSK symbol (one sample per symbol).  This can be an input from spread.py, or from decoding a DSSS spread signal using the PSK decoder in GNURADIO.  Note that by decoding DSSS as BPSK, you loose any processing gain benefits.  This method is very error prone if you are more than a few feet away (at least with my setup.)

You will need to manually "trim" the file before feeding it to the hex editor since the PSK decoder will spit out garbage before it receives a valid signal.  An easy way to trim the file is by opening the decoder output with a hex editor and searching for the PN sequence (remember, it may be inverted).  Trim at the beginning of the first PN sequence.

Consider using code/flowgraphs/decode.grc to output the necessary bitstream for this program.


rotate.py:
----------
Description: See description inside.


spread.py:
----------
Description: See description inside.
Usage: Provide this code with a command line argument consisting of binary representing a valid packet.  It will them manually spread it to a 1 sample/symbol series of bytes that can be fed into a GNURADIO PSK modulator.  This is useful if you desired to generate data to transmit. (Remember, transmitting is likely illegal.)  Remember that you can spread a BPSK signal by mixing it with the PN sequence and scaling up the data rate.


sync.py:
--------
Description: See description inside.
Usage: Supply sync.py with a iq file (interleaved floats representing i,q,i,q, etc..).  It will sequentially search for a corellation and then estimate the position of each corelation thereafter and attempt to track them.  It will then despread the signal and output a despread IQ file.  This IQ file can be fed back into GNURADIO for analysis.  Consider using code/flowgraphs/play_despread.grc to view the despread file and output a demodulated bitstream.


validatePacket.py:
------------------
Description: See description inside.
Usage: Provide packet data as a commandline argument to this program.  It will analyze the packet and determine if it is corrupt or not, and attempt to decode some of its contents.





----------------
code/flowgraphs/
----------------

4Mto5M.grc:
-----------
Description: Resamples a 4M iq signal to 5M using a rational resampler.  This is useful because with the USRP B200, we need to sample at an even mutiple of 32mhz.  For receiving Globalstar transmissions we also need to sample at an even mutiple of 1.25mhz (chip rate) and something greater than the Nyquist frequency of the signal (2 x 1.25mhz).  By sampling at 5mhz, we will receive a 4 sample/symbol signal (5mhz/1.25mhz).  Unfortuantely since 5mhz isnt a mutiple of 32mhz, we can sample at 4mhz (because 1.25*2 (nyquist) < 4mhz) and then resample to 5mhz.
Usage: Provide a 4mhz sampled IQ stream.  It will output a 5mhz resampled IQ stream.


capture_on_strong_signal.grc:
-----------------------------
Description:
Usage:


capture_to_file.grc:
--------------------
Description: This file will capture IQ data to file at a rate of 4mhz using a USRP B200.  It is set to tune to the appropriate Globalstar frequency.
Usage: Connect a USRP to GNURADIO and run the flowgraph.  Use it to capture a transmission.


decode.grc:
-----------
Description: This file takes in a IQ signal capture (from a Globalstar simplex packet) and decodes it to a bitstream.  This can be used to "cheat", and decode a spread BPSK signal, by just decoding it as high rate BPSK.  Note that you will receieve a bistream that contains the data mixed with the PN sequence and receive none of the processing gain benefits.  This only really works at close range.  A squelch is implented (and may need to be adjusted) so noise does not pass to the BPSK decoder.  This isnt exactly proper, but works great for testing.

Usage: Feed this flowgraph a IQ sample sample recording of a transmission.  It will output a bitstream.  This bitstream may need to be trimmed as described above before it is fed to code/standalone/despread.py


play_despread.grc:
------------------
Description: This flow graph is used to "play" a despread IQ file that was processed using code/standalone/sync.py. It the file despread successfully, you will observe a narrow peak in the middle of the FFT instead of the wideband spread signal.  This flowgraph will attempt to clean up the signal and output a bitstream.  Unfortuantely due to trouble with slow bitrates through the PSK decoder (we are trying to decode a 100 bit/second BPSK signal), we instead have to output from the decoder at 50 samples per symbol and post process accordingly.

Usage: Provide a despread file from sync.py.  It will output a bitstream of a decoded packet that can then be post processed.


transmit.grc:
-----------------------------
Description: This flowgraph could theoretically be used to transmit a Globalstar simplex packet.  Input is a spread set of symbols generated using code/standalone/spread.py.

 Note that transmitting is illegal and should not be done.  This code has NOT been tested and may be unreliable.  Please take the following issues into consideration. There is a chance that the GNURADIO provided PSK modulator may not be perfect for the job.  The GNURADIO modulator uses a RRC filter to shape the waveform.  The waveform from the simplex transmittors has not been shaped.  Also, given that the signal is being mixed to the carrier internally in the USRP, as far as I know, we do not have control over the alignment between the carrier and signal we are generating.  I believe that this timing is very important (IIRC, each PN transition needs to occur as the carrier wave transition).  However, I believe that eventually this will come into alignment and a packet will be successfully transmitted after a period of time.

Usage: Provide the flowgraph with a file containing spread binary symbols representing a packet.


replay.grc:
-----------
Description: This flowgraph can be used to replay a raw IQ recording.  Theoretically this could retrasmit a packet that was captured with sufficient signal strength.  Note that this has not been tested and it may be illegal to transmit.

Usage: Supply an IQ capture at the appropriate sample rate.


spread-modulate-transmit.grc:
-----------------------------
Description: This flowgraph contains a GNURADIO implementation of a PN sequence generator (GLFSR, configured to output the proper PN), and mixes it with packet data (provided as a .byte file, with each hex byte representing one binary bit).  The flowgraph upamples the packet data (using a custom block, code provided in the blocks folder), to generate a binary waveform before mixing with the PN sequence at the appropraite rate.  This data is then fed to the USRP where it is mixed with the carrier.  Note that theoretically this code will transmit a packet to the satellite, however this has not been tested and is illegal.  Please see the details of transmit.grc for edgecases that may cause issues.
Usage: Provide a file of 144 bytes containing packet data.


