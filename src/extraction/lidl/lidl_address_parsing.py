#!/usr/bin/env python
"""Extract the Addresses from Bing URLs and save them."""

import csv
import re
import urllib.parse as ul
from pathlib import Path

import pandas as pd
from rich import print
from tqdm import tqdm

# **************** Constants ****************

PATH_TO_BING_LINKS = Path("../../../data/raw/lidl/lidl_bing_links.txt")
PATH_TO_ADDRESS_CSV = Path("../../../data/lidl/lidl.csv")
PATH_TO_ADDRESS_PARQUET = Path("../../../data/lidl/lidl.parquet")

BING_RE = re.compile(
    r"""
    pos\.                                     # literal 'pos.'
    (?P<lat>[+-]?\d+\.\d+) _                  # latitude
    (?P<lon>[+-]?\d+\.\d+) _                  # longitude
    (?:[^_]*?-\+)?                            # optional 'Lidl+-' prefix
    (?P<street>.+?)                           # street (URL-encoded, may contain '+')
    (?:\+(?P<number>(?!\d{5}\+)[^+]+))?       # OPTIONAL house-number token
    \+(?P<postcode>\d{5})\+                   # German PLZ
    (?P<city>[^+]+)                           # city (URL-encoded)
""",
    re.VERBOSE,
)


# **************** Helper functions ****************


def read_bing_links(path: Path = PATH_TO_BING_LINKS) -> list[str]:
    """Reads the Bing links from a file.

    Args:
        path (optional): The path to the Bing links file. Defaults to
          PATH_TO_BING_LINKS.

    Returns:
        A list of Bing links.
    """
    with open(path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def parse_bing_link(bing_link: str) -> dict[str, str]:
    """Parses a Bing link using regex.

    Args:
        bing_link: The Bing link to parse.

    Returns:
        A dictionary containing the cleaned elements of a store address.

    Raises:
        ValueError: If there are no matches in the Bing link.
    """
    matches = BING_RE.search(bing_link)
    if not matches:
        raise ValueError(f"No matches found for link: {bing_link}")
    return {
        "Street": ul.unquote_plus(f"{matches['street']} {matches['number']}"),
        "Postalcode": matches["postcode"],
        "City": ul.unquote_plus(matches["city"]).strip(),
        "Latitude": matches["lat"],
        "Longitude": matches["lon"],
    }


def append_to_csv(row: dict[str, str], path: Path = PATH_TO_ADDRESS_CSV) -> None:
    """Appends a row (store data) to a csv file.

    Args:
        row: The row (address) data to append.
        path (optional): The path to the csv file. Defaults to
          PATH_TO_ADDRESS_CSV.
    """
    first_write = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if first_write:
            writer.writeheader()
        writer.writerow(row)


# **************** Main ****************


def main():
    """Runs the code."""
    # fetch all links
    bing_links = read_bing_links()
    addresses: list[dict[str, str]] = []
    # process and parse link
    for link in tqdm(bing_links, desc="parse Bing links"):
        address = parse_bing_link(link)
        append_to_csv(address)
        addresses.append(address)

    print("Successfully parsed all Bing links.")
    # create Dataframe and store it as parquet
    df = pd.DataFrame(addresses)
    df.to_parquet(PATH_TO_ADDRESS_PARQUET)
    print("Stored the results parquet file.")


if __name__ == "__main__":
    main()
