# The filter method is run once every time it recieves a new value from tracking

import numpy as np
import scipy as sp
import queue

# global variable as input
coeff = [1, 3, 5, 5]        # coefficient vector
N = len(coeff)      # Length of coefficient vector and length of input vector
input_vector = np.zeros(N)      # the same length as coefficients. Important = zero from beginning
output_vector_queue = queue.Queue()
input_vector_index = 0       # for knowing where the latest input value is in input_vector


# TODO Kolla på hur stor matrisen med tracking data blir. Ändras index efter ett tag

def filter(input_value):        # send input value
    input_vector[index] = input_value       # saves the input data in a vector continuously

    yn = 0          # to add all coefficients*values
    iterate_index = input_vector_index          # because variable value is changed in order to loop array
    for i in range(0,N-1):      # iterate over all coefficients and relevant input values
        if iterate_index-i < 0:         # if iterate_index is negative begin from right hand side and work our way to the left
            iterate_index = N+i-1       # moving to the rightmost location of array
        yn += coeff[i]*input_vector[iterate_index-i]        # add value of coefficient*data
    output_vector_queue.put(yn)         # put filtered data in output queue to send to SignalProcessing

    input_vector_index += 1      # Note index += 1 before if statement
    if input_vector_index == N:      #len(input_vector = N)
        index = 0