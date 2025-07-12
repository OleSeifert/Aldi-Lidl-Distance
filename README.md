# Aldi Lidl Distance

![python version](https://img.shields.io/badge/python-3.12-blue)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Static Badge](https://img.shields.io/badge/Code_License-MIT-green)
![Static Badge](https://img.shields.io/badge/Data_License-CC_BY--NC_4.0-lightgrey)

A quick project to answer the question:

> What is the maximal distance between any Aldi and the nearest Lidl store in Germany?

Inspired by a simple question at the Sunday breakfast table, I wanted to answer this question.

## Summary

>[!IMPORTANT]
> The answer to the question is: **114,465.6 meters** (or 114.4656 kilometers).
> That is the maximal distance from any Aldi store to the nearest Lidl store in Germany.
>
> I also computed some further stats on the minimal distances.
> The following metrics are calculated on the minimum distances from any Aldi store to the nearest Lidl store.
>
> | **Metric** | **Value** |
> | ---- | ---- |
> | Min | 36.651 meters |
> | Max | 114,465.6 meters |
> | Mean | 11,810.331 meters |
> | Median | 6,274.598 meters |
>
> (All values have been rounded to the third decimal place.)
>
> **Note:** I have calculated the direct distances.

## Code

### Data Extraction

The code to extract the data can be found in the `src/extraction` directory.
Here it is divided by the different store types (Aldi Süd, Aldi Nord, Lidl).
For each, I first extracted raw data, which were most often links to other sites.
The code is well documented, and from that, it should be understandable what is done.

### Data Analysis

The analysis can be found in the `src/analysis` directory.
At the moment, this only features the calculation of the nearest Lidl store for all Aldi stores (it also prints out the max/min/mean/median distances).
I see this as a work in progress and will add further analyses, if I find them interesting (or find the time).

## Data

The data was gathered using web scraping.
Mostly, it consisted of crawling different websites to find the addresses.
The `robots.txt` files allowed for the type of scraping that I did on all websites.

The way I was able to access the desired data was, however, different for each website.
In general, I recommend looking at the code.
It is well documented, and it should become clear what was done from that.
In the following, I will detail this a little bit.

### Aldi Sued

I started with Aldi Sued.
Here I was able to get the URLs for all stores via a `sitemap.xml` file.
For each of the store URLs, I was able to extract the needed information directly from the HTML.
It just needed a little parsing.

### Aldi Nord

Aldi Nord came second and was by far the easiest one to get all the addresses.
By watching the network connections on the website, I was able to identify an API that responded with all address information.
I just copied the JSON output to a file and needed to parse it for all stores.

### Lidl

For the Lidl addresses, I used an approach that was similar to the one used for Aldi Sued.
It involved obtaining the URLs of all cities (Lidl organizes their stores by city).
After that, the easiest way to obtain the address was by parsing their link/reference to Bing Maps.
For each store, they have a link on their page to Bing Maps for users to calculate the route.
From this URL I was able to obtain all the necessary information by parsing it using a regular expression.

## Installation

If you want to check out the code yourself, feel free to do so :smile:.

To install all dependencies without headaches, I recommend using [uv](https://docs.astral.sh/uv/).
Just install uv on your machine and navigate to the root directory of this project.
Run the command `uv sync`, and it should create a virtual environment with all dependencies installed for you.

## License

The code is licensed under the [MIT licence](./LICENSE).
The gathered data on Aldi and Lidl addresses is compliant with their terms of service.
Although it does not really "copyrightable", I licensed the data under the [CC BY 4.0 license](./LICENSE.data).

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png