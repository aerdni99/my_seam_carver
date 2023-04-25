"""
seamy.py

python seamy.py filename.pgm v_seams h_seams

filename.pgm - a pgm file
v_seams - number of vertical seams to remove
h_seams - number of horizontal seams to remove
"""

import pandas as pd
import sys

# Command lline arg handling

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
            if len(row) >= width:
                data.append(row[:width])
                row = row[width:]

image = pd.DataFrame(data)

def carve(height, width, image):
    energy = image.copy()
    seam_weights = image.copy()

    # Get the energy of each cell
    for x in range(height):
        for y in range(width):
            current_energy = 0
            if x - 1 != -1:
                current_energy += abs(image.iloc[x, y] - image.iloc[x - 1, y])
            if x + 1 != height:
                current_energy += abs(image.iloc[x, y] - image.iloc[x + 1, y])
            if y - 1 != -1:
                current_energy += abs(image.iloc[x, y] - image.iloc[x, y - 1])
            if y + 1 != width:
                current_energy += abs(image.iloc[x, y] - image.iloc[x, y + 1])
            energy.iloc[x, y] = current_energy

    # Build path weights
    for x in range(height):
        for y in range(width):
            seam_weights.iloc[x, y] = 0
    for x in range(height):
        for y in range(width):
            seam_weights.iloc[x, y] += energy.iloc[x, y]
            if x - 1 != -1:
                if y - 1 == -1:
                    seam_weights.iloc[x, y] += seam_weights.iloc[x - 1, [y, y + 1]].min()
                elif y + 1 == width:
                    seam_weights.iloc[x, y] += seam_weights.iloc[x - 1, [y - 1, y]].min()
                else:
                    seam_weights.iloc[x, y] += seam_weights.iloc[x - 1, [y - 1, y + 1]].min()

    # Traceback least energetic seam and remove
    min_weight = seam_weights.iloc[height - 1, 0]
    index = 0
    for y in range(width):
        if seam_weights.iloc[height - 1, y] < min_weight:
            index = y
            min_weight = seam_weights.iloc[height - 1, y]
    for y in range(width):
        if y >= index and y + 1 != width:
            image.iloc[height - 1, y] = image.iloc[height - 1, y + 1]

    for x in range(height - 1):
        path = ''
        if index - 1 != -1:
            min_weight = seam_weights.iloc[height - 2 - x, index - 1]
            path = 'left'
        else:
            min_weight = seam_weights.iloc[height - 2 - x, index]
            path = 'straight'
        if seam_weights.iloc[height - 2 - x, index] < min_weight:
            min_weight = seam_weights.iloc[height - 2 - x, index]
            path = 'straight'
        if index + 1 != width:
            if seam_weights.iloc[height - 2 - x, index + 1] < min_weight:
                path = 'right'
        if path == 'left':
            index -= 1
        elif path == 'right':
            index += 1
        for y in range(width):
            if y >= index and y + 1 != width:
                image.iloc[height - 2 - x, y] = image.iloc[height - 2 - x, y + 1]
    
    # Remove rightmost column
    image = image.iloc[:, :-1]
    return image


# Remove vertical seams
for seam in range(v_seams):
    image = carve(height, width, image)
    width -= 1


image = image.transpose()
# Remove horizontal seams
for seam in range(h_seams):
    image = carve(width, height, image)
    height -= 1

image = image.transpose()
# Write to output file
with open(fname, 'w') as f:
    # @TODO let the new height and width be reflected in the new header
    # @TODO persist comments from the input file
    f.write(literal + '\n')
    f.write(str(width) + ' ' + str(height) + '\n')
    f.write(str(max_val) + '\n')
    for index, row in image.iterrows():
        row_string = ' '.join([str(elem) for elem in row])
        f.write(row_string + '\n')
