#!/usr/bin/env python
"""Code to extract the addresses of Aldi Nord shops from a json dump.

The JSON dump was downloaded by me via this web address:
```
https://locator.uberall.com/api/storefinders-new/ALDINORDDE_UimhY3MWJaxhjK9QdZo3
Qa4chq1MAu/locations?v=20230110&language=de&locationIds=3180917&locationIds=3182
096&locationIds=3182160&locationIds=3182662&locationIds=3180455&locationIds=3180
456&locationIds=3180457&locationIds=3180458&locationIds=3180459&locationIds=3180
461&locationIds=3180462&locationIds=3180463&locationIds=3180464&locationIds=3180
465&locationIds=3180466&locationIds=3180468&locationIds=3180470&locationIds=3180
471&locationIds=3180472&locationIds=3180473&fieldMask=id&fieldMask=callToActions
&fieldMask=futureOpeningDate&fieldMask=openingHours&fieldMask=openNow&fieldMask=
nextOpen&fieldMask=phone&fieldMask=photos&fieldMask=specialOpeningHours&fieldMas
k=streetAndNumber&fieldMask=temporarilyClosedInfo
```
"""

import json
from typing import Any

import pandas as pd

# **************** Constants ****************

PATH_TO_JSON_DUMP = "../../../data/raw/aldi_nord/aldi_nord_raw.json"
PATH_TO_ADDRESS_CSV = "../../../data/aldi_nord/aldi_nord.csv"
PATH_TO_ADDRESS_PARQUET = "../../../data/aldi_nord/aldi_nord.parquet"

# **************** Helper functions ****************


def get_json_data(path: str) -> dict[str, str | dict[str, Any]]:
    """Reads the JSON file and returns it.

    Args:
        path: Path to the JSON file.

    Returns:
        The JSON file as a dictionary.
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_list_of_stores_from_json(
    json_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Gets the list of stores from the raw JSON.

    Args:
        json_data: The raw JSON data.

    Returns:
        A list of dictionaries. Each dictionary corresponds to one store.
    """
    return json_data["response"]["locations"]


def extract_information(store_list: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Extracts the address information from a list of stores.

    Each store is contained as a JSON object (dictionary).

    Args:
        store_list: The list of stores.

    Returns:
        A list of dictionaries, where each dictionary contains information about
        the address of a store.
    """
    rows = [
        {
            "Street": location["streetAndNumber"],
            "Postal Code": location["zip"],
            "City": location["city"],
            "Latitude": str(location.get("lat", "")),
            "Longitude": str(location.get("lng", "")),
        }
        for location in store_list
        if location.get("country", "") == "DE"  # Make sure the stores are in DE
    ]
    return rows


# **************** Main ****************


def main() -> None:
    """Runs the code."""
    # Get data
    data = get_json_data(PATH_TO_JSON_DUMP)

    # Get individual stores
    store_list = get_list_of_stores_from_json(data)

    # Parse the addresses from the stores
    address_list = extract_information(store_list)

    # save them
    df = pd.DataFrame(address_list)
    df.to_csv(PATH_TO_ADDRESS_CSV, index=False)
    df.to_parquet(PATH_TO_ADDRESS_PARQUET)
    print("Successfully saved the addresses to csv and parquet.")


if __name__ == "__main__":
    main()
