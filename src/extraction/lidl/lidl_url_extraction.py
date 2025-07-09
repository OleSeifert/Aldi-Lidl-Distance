#!/usr/bin/env python
"""Extract the URLs for the different LIDL stores."""

import logging
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rich import print
from tqdm import tqdm

# **************** Constants ****************

BASE_URL = "https://www.lidl.de"
FILIAL_SEARCH_URL = f"{BASE_URL}/f/"
PATH_LIDL_FILIALEN_URLS = Path("../../../data/raw/lidl/lidl_filialen_urls.txt")
PATH_BING_LINKS = Path("../../../data/raw/lidl/lidl_bing_links.txt")

HEADERS = {"User-Agent": "hobby-aldi-scraper/0.1"}
session = requests.Session()
session.headers.update(HEADERS)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# **************** Helper functions ****************


def extract_and_save_city_urls(
    url: str, path_to_save: Path = PATH_LIDL_FILIALEN_URLS
) -> None:
    """Extracts the city URLs for all cities and saves them to a file.

    Args:
        url: The URL of the LIDL Filialsuche.
        path_to_save (optional): The path of the txt file to save it. Defaults
          to PATH_LIDL_FILIALEN_URLS.
    """
    # fetch page
    res = requests.get(url, timeout=15)
    res.raise_for_status()

    # find all corresponding links
    soup = BeautifulSoup(res.text, "html.parser")
    city_div_list = soup.find_all(class_="ret-o-store-detail-city")

    with open(path_to_save, "w", encoding="utf-8") as file:
        # for each link get the href and attach it to the file
        for el in tqdm(city_div_list, desc="get the link and save it"):
            if el:
                # get a_tag (contains the href)
                a_tag = el.find("a")
                if a_tag and hasattr(a_tag, "get"):
                    href_content = a_tag.get("href")
                    if href_content:
                        url = f"{BASE_URL}{str(href_content)}"
                    else:
                        logging.warning(f"** No href found for div element: **\n{el}\n")

            # attach it to the file
            file.write(f"{url}\n")
        print("Successfully extracted and saved all city URLs.")


def extract_bing_links_for_city(city_url: str) -> list[str]:
    """Extracts the Bing Address Links for one city.

    Args:
        city_url: The city URL.

    Returns:
        A list of Bing links for this city.
    """
    res = session.get(city_url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    # Get all relevant elements
    rel_elems = soup.find_all("a", class_="ret-o-store-detail__store-icon-link")
    # filter list
    filtered_elems = [
        el
        for el in rel_elems
        if hasattr(el, "href") and el["href"].startswith("https://www.bing")
    ]
    # get the links
    links: list[str] = [el["href"] for el in filtered_elems]
    return links


def get_city_urls(path: Path = PATH_LIDL_FILIALEN_URLS) -> list[str]:
    """Reads the city URLs file.

    Args:
        path (optional): The path to the file. Defaults to PATH_LIDL_FILIALEN_URLS

    Returns:
        A list of city URLs.
    """
    # read file
    with open(path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def fetch_and_save_all_bing_links(
    path: Path = PATH_LIDL_FILIALEN_URLS, path_to_save: Path = PATH_BING_LINKS
) -> None:
    """Fetches and saves all Bing links for all cities.

    Args:
        path (optional): Path to City URLs. Defaults to PATH_LIDL_FILIALEN_URLS.
        path_to_save (optional): Path to save the Bing links. Defaults to
          PATH_BING_LINKS.

    Raises:
        ValueError: If the links for one city are completely empty.
    """
    # read all city urls
    city_urls = get_city_urls(path)
    bing_links: list[str] = []

    with open(path_to_save, "w", encoding="utf-8") as file:
        for city_u in tqdm(city_urls, desc="processing cities"):
            try:
                links = extract_bing_links_for_city(city_u)
                if not links:
                    raise ValueError(f"Empty links for city: {city_u}")
                bing_links += links
                file.write("\n".join(links) + "\n")
                file.flush()  # ensure data is written to disk immediately
                time.sleep(1.2)
            except Exception as e:
                print(f"Error processing city {city_u}: {e}")


# **************** Main ****************


def main() -> None:
    """Runs the code."""
    # Save the city urls
    # extract_and_save_city_urls(FILIAL_SEARCH_URL)

    # get all Bing links
    fetch_and_save_all_bing_links(PATH_LIDL_FILIALEN_URLS, PATH_BING_LINKS)


if __name__ == "__main__":
    main()
