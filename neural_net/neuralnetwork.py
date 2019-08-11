import numpy as np

class NeuralNetwork:

    def __init__(self, layer_sizes):
        self.num_layers = len(layer_sizes)
        self.layer_sizes = layer_sizes
        self.biases = [np.random.randn(y, 1) for y in layer_sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(layer_sizes[:-1], layer_sizes[1:])]

    def feedforward(self, a):
        for weight, bias in zip(self.weights, self.biases):
            a = activation_function(np.matmul(weight, a) + bias)
        return a

    def print_weights(self):
        for w in self.weights:
            print(w, '\n')

    def print_biases(self):
        for b in self.biases:
            print(b, '\n')

    def print_accuracy(self, images, labels):
        predictions = self.feedforward(images)
        num_correct = sum([np.argmax(a) == np.argmax(b) for a, b in zip(predictions, labels)])
        print('{0}/{1} accuracy: {2}%'.format(num_correct, len(images), num_correct/len(images)*100))

def activation_function(z):
    return 1/(1+np.exp(-z))

def activation_function_derivative(z):
    return activation_function(z)*(1-activation_function(z))
