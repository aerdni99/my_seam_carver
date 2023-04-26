"""
seamy.py

python seamy.py filename.pgm v_seams h_seams

filename.pgm - a pgm file
v_seams - number of vertical seams to remove
h_seams - number of horizontal seams to remove
"""

import pandas as pd
import sys
import time
import numpy as np

start = time.time()

# Command line arg handling

v_seams = int(sys.argv[2])
h_seams = int(sys.argv[3])
fname = sys.argv[1][:-4]
fname = fname + '_processed_' + str(v_seams) + '_' + str(h_seams) + ".pgm"

# Header values
literal = None
height = None
width = None
max_val = None

data = []
row = []


# .pgm parser
with open(sys.argv[1], 'r') as f:

    # Parse the header
    for line in f:
        if line.startswith('#'):
            continue
        if literal is None:
            literal = line.strip()
        elif width is None:
            width, height = map(int, line.split())
        elif max_val is None:
            max_val = int(line.strip())
        else:
            # Parse the data
            row = row + list(map(int, line.split()))
            if literal != 'P3':
                if len(row) >= width:
                    data.append(row[:width])
                    row = row[width:]
            else:
                if len(row) >= width * 3:
                    triples = [(row[i], row[i+1], row[i+2]) for i in range(0, len(row), 3)]
                    data.append(triples[:width])
                    row = row[width * 3:]

image = np.array(data)

def carve(height, width, image):
    energy = np.zeros((height, width))
    seam_weights = np.zeros((height, width))

    # Get the energy of each cell
    for x in range(height):
        for y in range(width):
            current_energy = 0
            if x - 1 != -1:
                current_energy += abs(image[x, y] - image[x - 1, y])
            if x + 1 != height:
                current_energy += abs(image[x, y] - image[x + 1, y])
            if y - 1 != -1:
                current_energy += abs(image[x, y] - image[x, y - 1])
            if y + 1 != width:
                current_energy += abs(image[x, y] - image[x, y + 1])
            energy[x, y] = current_energy

    # Build path weights
    for x in range(height):
        for y in range(width):
            seam_weights[x, y] = 0
    for x in range(height):
        for y in range(width):
            seam_weights[x, y] += energy[x, y]
            if x - 1 != -1:
                if y - 1 == -1:
                    seam_weights[x, y] += seam_weights[x - 1, [y, y + 1]].min()
                elif y + 1 == width:
                    seam_weights[x, y] += seam_weights[x - 1, [y - 1, y]].min()
                else:
                    seam_weights[x, y] += seam_weights[x - 1, [y - 1, y + 1]].min()

    # Traceback least energetic seam and remove
    min_weight = seam_weights[height - 1, 0]
    index = 0
    for y in range(width):
        if seam_weights[height - 1, y] < min_weight:
            index = y
            min_weight = seam_weights[height - 1, y]
    for y in range(width):
        if y >= index and y + 1 != width:
            image[height - 1, y] = image[height - 1, y + 1]

    for x in range(height - 1):
        path = ''
        if index - 1 != -1:
            min_weight = seam_weights[height - 2 - x, index - 1]
            path = 'left'
        else:
            min_weight = seam_weights[height - 2 - x, index]
        if seam_weights[height - 2 - x, index] < min_weight:
            min_weight = seam_weights[height - 2 - x, index]
            path = ''
        if index + 1 != width:
            if seam_weights[height - 2 - x, index + 1] < min_weight:
                path = 'right'
        if path == 'left':
            index -= 1
        elif path == 'right':
            index += 1
        for y in range(width):
            if y >= index and y + 1 != width:
                image[height - 2 - x, y] = image[height - 2 - x, y + 1]
    
    # Remove rightmost column
    image = image[:, :-1]
    return image

def carve_with_color(height, width, image):
    energy = np.zeros((height, width))
    seam_weights = np.zeros((height, width))

    # Get the energy of each cell
    for x in range(height):
        for y in range(width):
            current_energy = 0
            for rgb in range(3):
                if x - 1 != -1:
                    current_energy += abs(image[x, y, rgb] - image[x - 1, y, rgb])
                if x + 1 != height:
                    current_energy += abs(image[x, y, rgb] - image[x + 1, y, rgb])
                if y - 1 != -1:
                    current_energy += abs(image[x, y, rgb] - image[x, y - 1, rgb])
                if y + 1 != width:
                    current_energy += abs(image[x, y, rgb] - image[x, y + 1, rgb])
            energy[x, y] = current_energy

    # Build path weights
    for x in range(height):
        for y in range(width):
            seam_weights[x, y] = 0
    for x in range(height):
        for y in range(width):
            seam_weights[x, y] += energy[x, y]
            if x - 1 != -1:
                if y - 1 == -1:
                    seam_weights[x, y] += seam_weights[x - 1, [y, y + 1]].min()
                elif y + 1 == width:
                    seam_weights[x, y] += seam_weights[x - 1, [y - 1, y]].min()
                else:
                    seam_weights[x, y] += seam_weights[x - 1, [y - 1, y + 1]].min()

    # Traceback least energetic seam and remove
    min_weight = seam_weights[height - 1, 0]
    index = 0
    for y in range(width):
        if seam_weights[height - 1, y] < min_weight:
            index = y
            min_weight = seam_weights[height - 1, y]
    for y in range(width):
        if y >= index and y + 1 != width:
            image[height - 1, y] = image[height - 1, y + 1]

    for x in range(height - 1):
        path = ''
        if index - 1 != -1:
            min_weight = seam_weights[height - 2 - x, index - 1]
            path = 'left'
        else:
            min_weight = seam_weights[height - 2 - x, index]
        if seam_weights[height - 2 - x, index] < min_weight:
            min_weight = seam_weights[height - 2 - x, index]
            path = ''
        if index + 1 != width:
            if seam_weights[height - 2 - x, index + 1] < min_weight:
                path = 'right'
        if path == 'left':
            index -= 1
        elif path == 'right':
            index += 1
        for y in range(width):
            if y >= index and y + 1 != width:
                image[height - 2 - x, y] = image[height - 2 - x, y + 1]
    
    # Remove rightmost column
    image = image[:, :-1]
    return image

if literal == 'P3':
    fname = fname[:-3] + 'ppm'

if literal != 'P3':
    # Remove vertical seams
    for seam in range(v_seams):
        print("v_seam number", seam + 1)
        image = carve(height, width, image)
        width -= 1
    image = image.transpose()
    # Remove horizontal seams
    for seam in range(h_seams):
        print("h_seam number", seam + 1)
        image = carve(width, height, image)
        height -= 1
else:
    # Remove vertical seams
    for seam in range(v_seams):
        print("v_seam number", seam + 1)
        image = carve_with_color(height, width, image)
        width -= 1
    image = image.transpose()
    # Remove horizontal seams
    for seam in range(h_seams):
        print("h_seam number", seam + 1)
        image = carve_with_color(width, height, image)
        height -= 1

image = image.transpose()
# Write to output file
# with open(fname, 'w') as f:
#     # @TODO persist comments from the input file
#     f.write(literal + '\n')
#     f.write(str(width) + ' ' + str(height) + '\n')
#     f.write(str(max_val) + '\n')
#     np.savetxt(f, image.astype(int), fmt='%i', delimiter=' ', newline='\n')

end = time.time()

total = start - end
print()
print("time:", total)
print()
