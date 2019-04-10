import numpy as np

class Filter:
    def __init__(self,bla):
        self.coefficients = [7.7519e-05, -2.1943e-19, -0.00017507, -0.0002844, -0.0001234, 0.00030536, 0.00066201,
                             0.0004875, -0.00031655, -0.0011887, -0.0012209, 1.9897e-18, 0.0017329, 0.0023996,
                             0.00091246, -0.0020194, -0.0039765, -0.0026926, 0.001624, 0.0057127, 0.0055361,
                             -5.7122e-18, -0.007128, -0.0094788, -0.003479, 0.0074684, 0.014336, 0.0095102, -0.0056493,
                             -0.019686, -0.019019, 9.8548e-18, 0.024919, 0.033935, 0.01293, -0.029337, -0.061027,
                             -0.045529, 0.032296, 0.15036, 0.25711, 0.30003, 0.25711, 0.15036, 0.032296, -0.045529,
                             -0.061027, -0.029337, 0.01293, 0.033935, 0.024919, 9.8548e-18, -0.019019, -0.019686,
                             -0.0056493, 0.0095102, 0.014336, 0.0074684, -0.003479, -0.0094788, -0.007128, -5.7122e-18,
                             0.0055361, 0.0057127, 0.001624, -0.0026926, -0.0039765, -0.0020194, 0.00091246, 0.0023996,
                             0.0017329, 1.9897e-18, -0.0012209, -0.0011887, -0.00031655, 0.0004875, 0.00066201,
                             0.00030536, -0.0001234, -0.0002844, -0.00017507, -2.1943e-19, 7.7519e-05]
        self.coefficients_highpass = [7.7519e-05, -2.1943e-19, -0.00017507, -0.0002844, -0.0001234, 0.00030536, 0.00066201,
                             0.0004875, -0.00031655, -0.0011887, -0.0012209, 1.9897e-18, 0.0017329, 0.0023996,
                             0.00091246, -0.0020194, -0.0039765, -0.0026926, 0.001624, 0.0057127, 0.0055361,
                             -5.7122e-18, -0.007128, -0.0094788, -0.003479, 0.0074684, 0.014336, 0.0095102, -0.0056493,
                             -0.019686, -0.019019, 9.8548e-18, 0.024919, 0.033935, 0.01293, -0.029337, -0.061027,
                             -0.045529, 0.032296, 0.15036, 0.25711, 0.30003, 0.25711, 0.15036, 0.032296, -0.045529,
                             -0.061027, -0.029337, 0.01293, 0.033935, 0.024919, 9.8548e-18, -0.019019, -0.019686,
                             -0.0056493, 0.0095102, 0.014336, 0.0074684, -0.003479, -0.0094788, -0.007128, -5.7122e-18,
                             0.0055361, 0.0057127, 0.001624, -0.0026926, -0.0039765, -0.0020194, 0.00091246, 0.0023996,
                             0.0017329, 1.9897e-18, -0.0012209, -0.0011887, -0.00031655, 0.0004875, 0.00066201,
                             0.00030536, -0.0001234, -0.0002844, -0.00017507, -2.1943e-19, 7.7519e-05]
        self.length_of_input_vector = len(self.coefficients)  # Length of coefficient vector and length of input vector
        self.input_vector = np.zeros(self.length_of_input_vector)  # the same length as coefficients.
        self.input_vector_index = 0  # to know where the latest input value is in input_vector
        self.bla = bla

        sample_freq = 20
        length_seq = 100000
        sample_spacing = 1/sample_freq

        t = np.arange(length_seq)*sample_spacing
        signal_in = 4*np.sin(1 * 2.0*np.pi*t) + 0*np.sin(2 * 2.0*np.pi*t)
        signal_out = np.zeros(len(signal_in))

        for i in range(len(signal_in)):
            signal_out[i] = self.filter(signal_in[i])
        print(signal_out)




    def filter(self, input_value):  # send input value
        self.input_vector[self.input_vector_index] = input_value  # saves the input data in a vector continuously

        yn = 0  # to add all coefficients*values
        iterate_index = self.input_vector_index  # because variable value is changed in order to loop array
        for i in range(0, self.length_of_input_vector - 1):  # iterate over all coefficients and relevant input values
            if iterate_index - i < 0:  # if iterate_index is negative begin from right hand side and work our way to the left
                iterate_index = self.length_of_input_vector + i - 1  # moving to the rightmost location of array
            yn += self.coefficients[i] * self.input_vector[iterate_index - i]  # add value of coefficient*data
        # self.output_vector_queue.put(yn)  # put filtered data in output queue to send to SignalProcessing

        self.input_vector_index += 1  # Note index += 1 before if statement
        if self.input_vector_index == self.length_of_input_vector:  # len(input_vector = N)
            self.input_vector_index = 0
        return yn


###### MAIN ######
bla = 7
klass = Filter(bla)


