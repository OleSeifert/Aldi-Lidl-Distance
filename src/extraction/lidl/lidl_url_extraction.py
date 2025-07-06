#!/usr/bin/env python
"""Extract the URLs for the different LIDL stores."""

import logging

import requests
from bs4 import BeautifulSoup
from rich import print
from tqdm import tqdm

# **************** Constants ****************

BASE_URL = "https://www.lidl.de"
FILIAL_SEARCH_URL = f"{BASE_URL}/f/"
PATH_LIDL_FILIALEN_URLS = "../../../data/raw/lidl/lidl_filialen_urls.txt"

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


# TODO: Continue here. Extract these links and make sure they work. From these I can parse all needed information. Write regexes for them
example_link = "https://www.bing.com/mapspreview?rtp=~pos.48.82852_10.11375_Lidl+-+Ulmer+Str.+150+73431+Aalen"


def main() -> None:
    """Runs the code."""
    # Save the city urls
    # extract_and_save_city_urls(FILIAL_SEARCH_URL)


if __name__ == "__main__":
    main()
