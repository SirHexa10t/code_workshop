#!/usr/bin/python3

import json
import sys
import matplotlib.pyplot as plt
from dataclasses import dataclass
import colorsys

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Plot logarithmic calculation graphs")
    
    parser.add_argument('--title', type=str, dest='title', help='graph title', metavar='<whatever_you_call_it>', required=True)
    parser.add_argument('--x_label', type=str, dest='x_axis', help='horizontal axis title', metavar='<axis_description>', required=True)
    parser.add_argument('--y_label', type=str, dest='y_axis', help='vertical axis title', metavar='<axis_description>', required=True)
    parser.add_argument('--data_file', type=str, dest='datafile', help='file to read data from', metavar='<filepath>', required=True)
    
    return parser.parse_args()

args = parse_args()

@dataclass
class Datapoint:
    index: int
    measurement: float
    
@dataclass
class Dataset:
    label: str
    points: list[Datapoint]

    def get_x_values(self) -> list[int]:
        return [point.index for point in self.points]

    def get_y_values(self) -> list[float]:
        return [point.measurement for point in self.points]

def deserialize(data: str) -> Dataset:
    parsed = json.loads(data)
    label = list(parsed.keys())[0]  # More explicit than next(iter(parsed))
    points = [Datapoint(index=int(k), measurement=float(v)) for entry in parsed[label] for k, v in entry.items()]
    return Dataset(label=label, points=points)

def golden_angle_color_generator():
    golden_angle = (1 - 5**0.5) / 2  # golden ratio in radians
    hue = 0.0
    while True:
        yield colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
        hue += golden_angle

def marker_generator(labels):
    # markers = [
    #     ".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", 
    #     "s", "p", "*", "h", "H", "+", "x", "D", "d", "|", "_"
    # ]
    distinct_markers = [  # easier to distinguish
        ".", "o", ">",
        "s", "*", "+", "d"
    ]
    
    marker_repetitions = 1
    label_prefix_count = {}
    for l in labels:
        prefix = l.split('_')[0]
        label_prefix_count[prefix] = label_prefix_count.get(prefix, 0) + 1
    
    value_set = label_prefix_count.values()
    if len(set(value_set)) == 1:
        marker_repetitions = list(value_set)[0]
    
    i = 0
    while True:
        for j in range(marker_repetitions):
            yield distinct_markers[i]
        i=(i+1) % len(distinct_markers)


with open(args.datafile, 'r') as file:
    datasets = []
    for line in file:
        try:
            datasets.append(deserialize(line))
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing line: {line.strip()} - {e}", file=sys.stderr)

plt.figure(figsize=(10, 5))
color_gen = golden_angle_color_generator()
markers_gen = marker_generator([d.label for d in datasets])
for dataset in sorted(datasets, key=lambda x: x.label):  # insert by alphabetical order of labels
    plt.plot(dataset.get_x_values(), dataset.get_y_values(), marker=next(markers_gen), markersize=10, markeredgecolor='black', label=dataset.label, color=next(color_gen))

plt.xlabel(f"Logarithmic {args.x_axis}")
plt.ylabel(f"Logarithmic {args.y_axis}")
plt.title(args.title)
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.grid(True)

plt.show()
