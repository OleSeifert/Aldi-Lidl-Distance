#!/usr/bin/env python
"""Extraction of the store addresses of the ALDI Sued stores."""

import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich import print

# **************** Constants ****************

ALDI_SUED_URLS = "../../data/cleaned_aldi_store_urls.txt"
HEADERS = {"User-Agent": "hobby-aldi-scraper/0.1"}

session = requests.Session()
session.headers.update(HEADERS)


def read_urls(path: str) -> list[str]:
    """Reads the URLs from the file.

    Args:
        path: _description_

    Returns:
        _description_
    """
    with open(path, "r") as file:
        lines = file.readlines()

        # Clean '\n'
        lines = [line.strip() for line in lines]

    return lines


def get_soup(url: str) -> BeautifulSoup:
    """Fetches page and returns BeautifulSoup object.

    Args:
        url: The URL to fetch.

    Returns:
        A BeautifulSoup object of the fetched page.
    """
    r = session.get(url, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def parse_store(store_url: str) -> dict[str, str]:
    """Fetches the data for a single store.

    Args:
        store_url: The URL of the store.

    Returns:
        A dictionary containing the address information.

    Raises:
        ValueError: If some of the attributes do not exist.
    """
    soup = get_soup(store_url)

    def get_text_or_raise(selector: str) -> str:
        """Fetches element and checks if it exists."""
        element = soup.find(class_=selector)

        if element and element.text.strip():
            return element.text.strip()
        else:
            raise ValueError(f"Missing or empty {selector} for store: {store_url}")

    street = get_text_or_raise("Address-line1")
    postal_code = get_text_or_raise("Address-postalCode")
    city = get_text_or_raise("Address-city")

    coordinates = soup.select_one('meta[name="geo.position"]')
    if coordinates:
        latitude, longitude = str(coordinates.get("content")).split(";")
    else:
        raise ValueError(f"No coordinates for store: {store_url}")

    return {
        "street": street,
        "postalcode": postal_code,
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
        "url": store_url,
    }


def main() -> None:
    """Runs the code."""
    urls = read_urls(ALDI_SUED_URLS)

    addresses: list[dict[str, str]] = []

    for url in urls:
        address = parse_store(url)
        addresses.append(address)
        time.sleep(0.75)

    df = pd.DataFrame(addresses)
    print(df)

    # Save code to a csv
    df.to_parquet("../../data/aldi_sued.parquet")
    df.to_csv("../../data/aldi_sued.csv")


if __name__ == "__main__":
    main()
