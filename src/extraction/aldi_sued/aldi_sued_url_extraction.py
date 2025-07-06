#!/usr/bin/env python
"""Contains the code to extract the urls of the ALDI Sued shops.

In the cleaned URLs there where two or three that made problems. These have been
cleaned out by hand. The `cleaned_aldi_sued_store_urls.txt` file is the one that
was used for the crawling.
"""

import xml.etree.ElementTree as ET

import requests

# **************** Constants ****************

SITEMAP_PATH = ""
RAW_STORE_URLS_PATH = ""
CLEANED_STORE_URLS_PATH = ""

SM_URL = "https://filialen.aldi-sued.de/sitemap.xml"

# **************** Helper functions ****************


def save_sitemap_xml(sm_url: str, path_to_file: str) -> None:
    """Fetches and saves the XML sitemap.

    Args:
        sm_url: URL of the sitemap file.
        path_to_file: Path to the location where file should be saved.
    """
    xml_text = requests.get(SM_URL, timeout=20).text

    with open(path_to_file, "w", encoding="utf-8") as file:
        file.write(xml_text)


def fetch_root_and_parse(sm_url: str) -> ET.Element:
    """Fetches and parses the Sitemap.

    Args:
        sm_url: The URL of the sitemap file.

    Returns:
        A parsed Element of the XML file.
    """
    xml_text = requests.get(SM_URL, timeout=20).text

    return ET.fromstring(xml_text)


def extract_and_save_store_urls(sitemap: ET.Element, path: str) -> list[str]:
    """Extracts and saves the store URLs.

    Args:
        sitemap: The parsed element of the XML sitemap.
        path: The path where the file should be stored.

    Returns:
        The list of store URLs.
    """
    # define namespace
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Extract store urls
    store_urls = [loc.text for loc in sitemap.findall(".//sm:loc", namespace)]
    # clean for none
    store_urls = [url for url in store_urls if url is not None]

    # Save to txt file, one URL per line
    with open(path, "w", encoding="utf_8") as file:
        file.write("\n".join(store_urls))

    return store_urls


def drop_prefixes(urls: list[str]) -> list[str]:
    """Drops URLs which are a strict prefix of other URLs.

    The ALDI URLs are structured in a way that there exist also URLs for groups
    of stores. This is bad, because we want to extract information that is only
    available on the single store pages. The URLs are however structured in such
    a way, that the 'store overview' pages are a prefix of the 'single store'
    pages. Therefore we drop the prefixes.

    Args:
        urls: A list of URLs to search for prefixes in.

    Returns:
        The list without prefixes.
    """
    pool = set(urls)
    to_remove = set()

    for link in urls:
        # Check all prefixes
        for i in range(1, len(link)):
            prefix = link[:i]
            if prefix in pool:
                to_remove.add(prefix)

    return [link for link in urls if link not in to_remove]


def save_cleaned_urls(cleaned_urls: list[str], path: str) -> None:
    """Saves a list of cleaned URLs to a file.

    Args:
        cleaned_urls: The list of cleaned URLs.
        path: The path to save the file to.
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(cleaned_urls))


# **************** Main ****************


def main() -> None:
    """Runs the code."""
    # Save the sitemap
    save_sitemap_xml(SM_URL, SITEMAP_PATH)

    # Fetch the sitemap
    sm_root = fetch_root_and_parse(SM_URL)

    # Extract and save store urls
    store_urls = extract_and_save_store_urls(sm_root, RAW_STORE_URLS_PATH)

    # Clean the prefixes and save them
    cleaned_urls = drop_prefixes(store_urls)

    # Save cleaned list
    save_cleaned_urls(cleaned_urls, CLEANED_STORE_URLS_PATH)


if __name__ == "__main__":
    main()
