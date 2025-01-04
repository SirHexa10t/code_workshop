import json
import sys
import matplotlib.pyplot as plt
from dataclasses import dataclass
import colorsys

@dataclass
class Dataset:
    label: str
    points: list[dict[int, float]]

    def get_x_values(self) -> list[int]:
        return [int(list(point.keys())[0]) for point in self.points]

    def get_y_values(self) -> list[float]:
        return [float(list(point.values())[0]) for point in self.points]

def deserialize(data: str) -> Dataset:
    parsed = json.loads(data)
    label = list(parsed.keys())[0]  # More explicit than next(iter(parsed))
    points = [{int(k): float(v)} for entry in parsed[label] for k, v in entry.items()]
    return Dataset(label=label, points=points)

def golden_angle_color_generator():
    golden_angle = (1 - 5**0.5) / 2  # golden ratio in radians
    hue = 0.0
    while True:
        yield colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
        hue += golden_angle


with open(sys.argv[1], 'r') as file:
    title = file.readline().strip()
    y_axis = file.readline().strip()
    x_axis = file.readline().strip()
    
    datasets = []
    for line in file:
        try:
            datasets.append(deserialize(line))
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing line: {line.strip()} - {e}", file=sys.stderr)

plt.figure(figsize=(10, 5))
color_gen = golden_angle_color_generator()
for dataset in datasets:
    color = next(color_gen)
    plt.plot(dataset.get_x_values(), dataset.get_y_values(), marker='o', label=dataset.label, color=color)

plt.xlabel(f"Logarithmic {x_axis}")
plt.ylabel(f"Logarithmic {y_axis}")
plt.title(title)
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.grid(True)

plt.show()