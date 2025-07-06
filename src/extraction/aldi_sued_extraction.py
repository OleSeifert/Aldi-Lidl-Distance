#!/usr/bin/env python
"""Extraction of the store addresses of the ALDI Sued stores."""

import csv
import logging
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# **************** Constants ****************

ALDI_SUED_URLS = "../../data/cleaned_aldi_store_urls.txt"
HEADERS = {"User-Agent": "hobby-aldi-scraper/0.1"}
PATH_TMP = Path("../../data/aldi_sued_addresses_tmp.csv")

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


def append_to_csv(row: dict[str, str], path: Path) -> None:
    """Appends a row (store data) to a csv file.

    Args:
        row: The row (address) data to append.
        path: The path to the csv file.
    """
    first_write = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if first_write:
            writer.writeheader()
        writer.writerow(row)


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
    # Setup logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    urls = read_urls(ALDI_SUED_URLS)
    addresses: list[dict[str, str]] = []

    logging.info("Start crawling the addresses.")

    # Fetch each address append it to the tmp csv and add them
    for url in tqdm(urls, desc="crawl stores"):
        address = parse_store(url)
        append_to_csv(address, PATH_TMP)
        addresses.append(address)
        time.sleep(0.75)  # Polite pause for the request

    logging.info("Successfully crawled all store addresses.")

    # Create dataframe and store it as both csv and parquet
    df = pd.DataFrame(addresses)
    df.to_parquet("../../data/aldi_sued.parquet")
    df.to_csv("../../data/aldi_sued.csv")
    logging.info("Stored the results as parquet and csv files.")


if __name__ == "__main__":
    main()
