#!/usr/bin/env python
"""Code to compute the minimum distances between all Aldi-Lidl pairs."""

import statistics
from pathlib import Path

import pandas as pd
from geopy.distance import geodesic
from rich import print
from tqdm import tqdm

# **************** Constants ****************

PATH_TO_ALDI_SUED = Path("../../data/aldi_sued/aldi_sued.csv")
PATH_TO_ALDI_NORD = Path("../../data/aldi_nord/aldi_nord.csv")
PATH_TO_LIDL = Path("../../data/lidl/lidl.csv")
PATH_TO_MIN_DISTANCES = Path("../../data/min_distances.txt")

# **************** Helpers ****************


def read_and_concat_aldi_coords(
    aldi_sued_path: Path = PATH_TO_ALDI_SUED, aldi_nord_path: Path = PATH_TO_ALDI_NORD
) -> list[tuple[float, float]]:
    """Reads and concatenates Aldi Sued and Nord coordinates.

    Args:
        aldi_sued_path (optional): The path to the Aldi Sued addresses. Defaults
          to PATH_TO_ALDI_SUED.
        aldi_nord_path (optional): The path to the Aldi Nord addresses. Defaults
          to PATH_TO_ALDI_NORD.

    Returns:
        A list of tuples, where each tuple contains the latitude and longitude
        coordinates as floats.
    """
    aldi_coordinates: list[tuple[float, float]] = []
    # Aldi sued coordinates
    aldi_sued_df = pd.read_csv(aldi_sued_path)
    aldi_sued_coordinates = [
        (float(row["Latitude"]), float(row["Longitude"]))
        for _, row in aldi_sued_df.iterrows()
    ]
    # Aldi nord coordinates
    aldi_nord_df = pd.read_csv(aldi_nord_path)
    aldi_nord_coordinates = [
        (float(row["Latitude"]), float(row["Longitude"]))
        for _, row in aldi_nord_df.iterrows()
    ]
    aldi_coordinates = aldi_sued_coordinates + aldi_nord_coordinates
    return aldi_coordinates


def read_lidl_coords(filepath: Path = PATH_TO_LIDL) -> list[tuple[float, float]]:
    """Read the lidl coordinates.

    Args:
        filepath (optional): The path to the Lidl addresses. Defaults to
          PATH_TO_LIDL.

    Returns:
        A list of tuples where each tuple contains the latitude and longitude
        coordinates for a Lidl store.
    """
    lidl_df = pd.read_csv(filepath)
    lidl_coordinates = [
        (float(row["Latitude"]), float(row["Longitude"]))
        for _, row in lidl_df.iterrows()
    ]
    return lidl_coordinates


def calculate_min_distances(
    aldi_coords: list[tuple[float, float]], lidl_coords: list[tuple[float, float]]
) -> list[float]:
    """Calculates the distance for all Aldis to the nearest Lidl.

    Args:
        aldi_coords: The coordinates of Aldi stores.
        lidl_coords: The coordinates of Lidl stores.

    Returns:
        A list containing the distance, in meters, to the nearest Lidl store for
        each Aldi store. Both Aldi nord and Aldi sued store.
    """
    min_distances: list[float] = []
    for aldi in tqdm(aldi_coords, desc="computing distances for Aldis"):
        distances: list[float] = []
        for lidl in lidl_coords:
            dist = geodesic(aldi, lidl).meters
            distances.append(dist)
        # check the minimal one and append it to global list
        min_distances.append(min(distances))
    return min_distances


def save_min_distances(
    min_distances: list[float], path_to_save: Path = PATH_TO_MIN_DISTANCES
) -> None:
    """Saves the minimum distances to a file.

    Each distance is saved in a new line in a txt file.

    Args:
        min_distances: The list of minimum distances (in meters) for all Aldi
          stores.
        path_to_save (optional): The filepath where the distances should be
          saved. Defaults to PATH_TO_MIN_DISTANCES.
    """
    with open(path_to_save, "w", encoding="utf-8") as file:
        file.writelines("\n".join(str(distance) for distance in min_distances))


# **************** Main ****************


def main() -> None:
    """Runs the code."""
    # get Aldi coordinates
    aldi_coordinates = read_and_concat_aldi_coords()
    # get lidl_coordinates
    lidl_coordinates = read_lidl_coords()
    # compute the minimum distances
    minimum_distances = calculate_min_distances(aldi_coordinates, lidl_coordinates)
    # save them to a file
    save_min_distances(minimum_distances)
    print(
        f"The maximal distance between any Aldi and a Lidl in Germany is at most {max(minimum_distances)} meters."
    )

    print(f"Nearest Lidl to an Aldi {min(minimum_distances)} meters")
    print(
        f"Median distance from an Aldi to a Lidl: {statistics.median(minimum_distances)} meters"
    )
    print(
        f"Mean distance from an Aldi to a Lidl: {statistics.mean(minimum_distances)} meters"
    )


if __name__ == "__main__":
    main()
