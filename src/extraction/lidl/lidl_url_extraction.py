#!/usr/bin/env python
"""Extract the URLs for the different LIDL stores."""

import logging
import time

import requests
from bs4 import BeautifulSoup
from rich import print
from tqdm import tqdm

# **************** Constants ****************

BASE_URL = "https://www.lidl.de"
FILIAL_SEARCH_URL = f"{BASE_URL}/f/"
PATH_LIDL_FILIALEN_URLS = "../../../data/raw/lidl/lidl_filialen_urls.txt"
PATH_BING_LINKS = "../../../data/raw/lidl/lidl_bing_links.txt"


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def extract_and_save_city_urls(
    url: str, path_to_save: str = PATH_LIDL_FILIALEN_URLS
) -> None:
    """Extracts the city URLs for all cities and saves them to a file.

    Args:
        url: The URL of the LIDL Filialsuche.
        path_to_save (optional): The path of the txt file to save it. Defaults
          to PATH_LIDL_FILIALEN_URLS.
    """
    # fetch page
    res = requests.get(FILIAL_SEARCH_URL, timeout=15)
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
    res = requests.get(city_url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    # Get all relevant elements
    rel_elems = soup.find_all("a", class_="ret-o-store-detail__store-icon-link")
    # filter list
    filtered_elems = [
        el
        for el in rel_elems
        if hasattr(el, "href") and el["href".startswith("https://www.bing")]
    ]
    # get the links
    links: list[str] = [el["href"] for el in filtered_elems]
    return links


def get_city_urls(path: str = PATH_LIDL_FILIALEN_URLS) -> list[str]:
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
    path: str = PATH_LIDL_FILIALEN_URLS, path_to_save: str = PATH_BING_LINKS
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
    for city_u in city_urls:
        # get the links
        links = extract_bing_links_for_city(city_u)
        # check whether links are empty
        if not links:
            raise ValueError(f"Emtpy links for city: {city_u}")

        bing_links += links
        time.sleep(1.2)

    # save to file
    with open(path_to_save, "w", encoding="utf-8") as file:
        file.write("\n".join(bing_links))


# TODO: write parser for these links to extract address, (lat, long) from them. use regex
example_link = "https://www.bing.com/mapspreview?rtp=~pos.48.82852_10.11375_Lidl+-+Ulmer+Str.+150+73431+Aalen"


def main() -> None:
    """Runs the code."""
    # Save the city urls
    # extract_and_save_city_urls(FILIAL_SEARCH_URL)

    # TODO: run the function below
    # fetch_and_save_all_bing_links(PATH_LIDL_FILIALEN_URLS, PATH_BING_LINKS)


if __name__ == "__main__":
    main()
