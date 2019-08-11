'''
layers = (2,3,3,5)
1   2   3   4

            x
x   x   x   x
    x   x   x
x   x   x   x
            x

'''


import neuralnetwork as nn
import numpy as np

with np.load('mnist.npz') as data:
    training_images = data['training_images']
    training_labels = data['training_labels']


layer_sizes = (2, 3, 3, 5)
net = nn.NeuralNetwork(layer_sizes)

print(nn.activation_function(3)*(1-nn.activation_function(3)))