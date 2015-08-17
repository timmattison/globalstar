/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "digitalresample_ff_impl.h"

#include <stdio.h>


namespace gr {
  namespace mytest {

    digitalresample_ff::sptr
    digitalresample_ff::make(const int interpamount)
    {
      return gnuradio::get_initial_sptr
        (new digitalresample_ff_impl(interpamount));
    }

    /*
     * The private constructor
     */
    digitalresample_ff_impl::digitalresample_ff_impl(const int interpamount)
      : gr::sync_interpolator("digitalresample_ff",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)), interpamount),
              interp_number(interpamount)
    {}

    /*
     * Our virtual destructor.
     */
    digitalresample_ff_impl::~digitalresample_ff_impl()
    {
    }

    int
    digitalresample_ff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = (const float *) input_items[0];
        float *out = (float *) output_items[0];

        // Do <+signal processing+>

        for (int i = 0; i < noutput_items / interp_number; i++) {
          out[i*interp_number ] = in[i]; 
          out[i*interp_number + 1] = in[i]; 
          out[i*interp_number + 2] = in[i];


           for (int j = 0; j < interp_number; j++) { 
                out[interp_number*i + j] = in[i]; 
            }


        }

        //printf("%d\n",interp_number);

        // Tell runtime system how many output items we produced.
        //return noutput_items;
        return noutput_items;

    }

  } /* namespace mytest */
} /* namespace gr */

