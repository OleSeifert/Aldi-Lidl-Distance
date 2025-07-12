#!/usr/bin/env python
"""Prints the max/min/mean/median statistics of the distances.

These are from any Aldi store to the nearest Lidl store.
"""

import statistics
from pathlib import Path
from rich import print

PATH_TO_MIN_DISTANCES = Path("../../data/min_distances.txt")


def main() -> None:
    """Runs the code."""
    with open(PATH_TO_MIN_DISTANCES, "r", encoding="utf-8") as file:
        distances = [float(line.strip()) for line in file.readlines()]

    # Calculate the stats
    min_ = min(distances)
    max_ = max(distances)
    mean = statistics.mean(distances)
    median = statistics.median(distances)
    # print the stats
    print(f"The minimal distance is: {min_} meters.")
    print(f"The maximum distance is: {max_} meters.")
    print(f"The mean distance is: {mean} meters.")
    print(f"The median distance is: {median} meters.")


if __name__ == "__main__":
    main()
