'''
module for creating images in command line and producing histogram from them
'''

import random

PIXELS = ['*', '#', '@', '&', '$', '%']
HEIGHT = 10
WIDTH = 15*2

class RandomImage():
    '''
    class containing image data
    '''
    def __init__(self, height, width, pixels):
        self.height = height
        self.width = width
        self.pixels = pixels
        self.image = [[] for i in range(height)]
        self.fill_image()

    def generate_random_pixel(self):
        return self.pixels[random.randrange(len(self.pixels))]

    def fill_image(self):
        for row in self.image:
            for cell in range(self.width):
                row.append(self.generate_random_pixel())

    def __str__(self):
        return "\n".join("".join(row) for row in self.image)

class Histogram():
    '''
    class containing histogram data
    '''
    def __init__(self, image):
        self.image = image
        self.data = dict.fromkeys([cell for row in image.image for cell in row], 0)
        for row in image.image:
            for cell in row:
                self.data[cell] += 1

    def __str__(self):
        for pixel in self.data:
            if pixel == list(self.data.keys())[-1]:
                return pixel + ' ' + '='*self.data[pixel]
            else:
                print(pixel + ' ' + '='*self.data[pixel])


img = RandomImage(HEIGHT, WIDTH, PIXELS)
print(img)
his = Histogram(img)
print(his)

'''
function version of histogram.py
'''
# print(histo)
# def create_RandomImage(height, width, pixels):
#     image = []
#     for row in range(HEIGHT):
#         image.append([])
#     for row in image:
#         for cell in range(WIDTH):
#             row.append(pixels[random.randrange(len(pixels))])
#     return image

# def print_image(image):
#     for row in image:
#         for cell in row:
#             sys.stdout.write(cell)
#         print()



# def create_histogram(image):
#     histogram = dict.fromkeys([cell for row in image for cell in row], 0)
#     for row in image:
#         for cell in range(len(row)):
#             histogram[row[cell]]+=1
#     return histogram

# def print_histogram(histogram):
#     for pixel in histogram:
#         print(pixel + ' ' + '='*histogram[pixel])


# image = create_RandomImage(HEIGHT, WIDTH, PIXELS)
# print_image(image)
# histogram = create_histogram(image)
# print_histogram(histogram)

