"""
seamy.py

This is where it all starts
"""

import pandas as pd
import sys

# Command lline arg handling

h_seams = int(sys.argv[2])
v_seams = int(sys.argv[3])
fname = sys.argv[1][:-4]
fname = fname + '_processed_' + str(h_seams) + '_' + str(v_seams) + ".pgm"

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
                data.append(row[:40])
                row = row[40:]


df = pd.DataFrame(data)
df = df.transpose()

# Write to output file

with open(fname, 'w') as f:
    # @TODO let the new height and width be reflected in the new header
    # @TODO persist comments from the input file
    f.write(literal + '\n')
    f.write(str(width) + ' ' + str(height) + '\n')
    f.write(str(max_val) + '\n')
    for index, row in df.iterrows():
        row_string = ' '.join([str(elem) for elem in row])
        f.write(row_string + '\n')

