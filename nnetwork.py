# I created this program to construct the network model described in Rumelhart et al. (1986).

# The network trains itself by repeatedly propogating the error on a training dataset back
# through the network, calculating partial derivatives, and incrementally adjusting the 
# network's parameters.

# Rumelhart, D., Hinton, G. & Williams, R., Learning representations by back-propagating errors. Nature 323, 533–536 (1986). 
# http://www.cs.toronto.edu/~hinton/absps/naturebp.pdf

import numpy as np
            
class Neuron: 
    
    def __init__(self, neuron_idx, layer_below):
        self.neuron_idx = neuron_idx   
        self.output = []
        self.validation = []
        self.testresults = []
        self.layer_below = layer_below
        if self.layer_below is not None:
            np.random.seed(1234)
            self.weights = np.random.randn(self.layer_below.num_neurons + 1)
        else: 
            self.weights = []   
            
    def activate_neuron(self):
        y_in = self.layer_below.get_output()
        y_in = np.concatenate((y_in,np.ones((y_in.shape[0],1))),axis=1) # add bias term
        w = self.weights
        x = y_in.dot(w) # formula (1)
        y_out = 1 / (1 + np.exp(-x)) # formula (2): sigmoid activation function
        self.output = y_out

    def validate(self):
        v_in = self.layer_below.get_validation()
        v_in = np.concatenate((v_in,np.ones((v_in.shape[0],1))),axis=1)
        w = self.weights
        x = v_in.dot(w)
        y_out = 1 / (1 + np.exp(-x)) 
        self.validation = y_out
        
    def results(self):
        y_in = self.layer_below.get_results()
        y_in = np.concatenate((y_in,np.ones((y_in.shape[0],1))),axis=1) 
        w = self.weights
        x = y_in.dot(w)
        y_out = 1 / (1 + np.exp(-x))
        self.testresults = y_out
        
    def compute_derivatives(self, dEdy_out, learning_rate):
        dEdy_out = dEdy_out.reshape(dEdy_out.shape[0],-1)
        dEdy_out = dEdy_out[:,self.neuron_idx]
        dy_outdx = self.output*(1-self.output) # formula (5)
        y_in = self.layer_below.get_output()
        y_in = np.concatenate((y_in,np.ones((y_in.shape[0],1))),axis=1) # add bias term
        w = self.weights
        dxdw = y_in
        dxdy_in = w
        a = np.transpose([dEdy_out]*dxdw.shape[1])
        b = np.transpose([dy_outdx]*dxdw.shape[1])
        dEdw = a * b * dxdw # formula (6)
        self.dEdy_in = a * b * dxdy_in # formula (7)
        self.weights = self.weights - learning_rate * dEdw.mean(axis=0) # formula (8)
    
class Layer:  
    
    def __init__(self, num_neurons, layer_below=None, input_data=None, validation_data=None, test_data=None):
        self.num_neurons = num_neurons
        self.layer_below = layer_below
        self.input_data = input_data
        self.validation_data = validation_data
        self.neurons = []
        for neuron_idx in range(self.num_neurons):
            self.neurons.append(Neuron(neuron_idx, self.layer_below))
            if input_data is not None:
                self.neurons[neuron_idx].output = input_data[:,neuron_idx]
            if validation_data is not None:
                self.neurons[neuron_idx].validation = validation_data[:,neuron_idx]
            if test_data is not None:
                self.neurons[neuron_idx].testresults = test_data[:,neuron_idx]
        if self.layer_below is not None:
            self.layer_below.layer_above = self

    def set_neurons(self):
        for neuron in self.neurons:
            neuron.layer_below = self.layer_below

    def activate_layer(self):
        for neuron in self.neurons:
            neuron.activate_neuron()
            neuron.validate()
            neuron.results()

    def get_output(self):
        y_out = np.transpose([y.output for y in self.neurons])
        return y_out
    
    def get_validation(self):
        validation = np.transpose([y.validation for y in self.neurons])
        return validation
    
    def get_results(self):
        results = np.transpose([y.testresults for y in self.neurons])
        return results
        
    def back_propagate(self, dEdy_out, learning_rate):
        for neuron in self.neurons:
            neuron.compute_derivatives(dEdy_out, learning_rate)
        dEdy_in = sum([x.dEdy_in for x in self.neurons])
        return dEdy_in
    
class NeuralNet:
    
    def __init__(self, layers):
        self.layers = layers
        self.errors = []
        self.valerrors = []
        self.testerrors = []
   
    def learn(self, num_epochs, y_train, y_validate, y_test):
  
        def check_val_stop(valerrors):
            stop = False
            checknum = 50
            if len(valerrors)>checknum:
                stop = True
                vals = valerrors[-1*checknum:]
                for e in vals[1:]:
                    if e < vals[0]:
                        stop = False
            return stop

        for epoch in range(num_epochs):
            
            if check_val_stop(self.valerrors)==False:
            
                for layer in self.layers[1:]:
                    layer.activate_layer()
                
                dEdy_out = self.layers[-1].get_output()[:,0] - y_train # formula (4)
                for layer in reversed(self.layers[1:]):
                    dEdy_out = layer.back_propagate(dEdy_out, learning_rate=0.01)
                
                error = np.sqrt(np.square(self.layers[-1].get_output()[:,0] - y_train).mean())
                self.errors.append(error)
                
                valerror = np.sqrt(np.square(self.layers[-1].get_validation()[:,0] - y_validate).mean())
                self.valerrors.append(valerror)
        
                testerror = np.sqrt(np.square(self.layers[-1].get_results()[:,0] - y_test).mean())
                self.testerrors.append(testerror)
        
