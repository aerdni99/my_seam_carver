"""
seamy.py

This is where it all starts
"""

import pandas as pd
import sys

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

print(df)
print(width, 'x', height)