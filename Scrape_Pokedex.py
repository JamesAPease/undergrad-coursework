"""
Pokédex Scraper
===============

Scrapes Pokédex number and name lists from Serebii.net into CSV files, used as
the master list for a personal shiny living-dex tracker.

Includes a polite delay between requests and validates the result so a site
layout change fails loudly instead of writing an empty file.

Usage
    python scrape_pokedex.py
"""

import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (personal Pokédex tracker)"}

DEXES = {
    "national_dex.csv": "https://www.serebii.net/pokemon/nationalpokedex.shtml",
    "gen8_dex.csv": "https://www.serebii.net/pokemon/gen8pokemon.shtml",
}


def scrape_dex(url: str, delay: float = 2.0) -> pd.DataFrame:
    """Return a DataFrame of Pokédex numbers and names from one Serebii dex page."""
    time.sleep(delay)  # be polite to a fan-run site
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="dextable")
    if table is None:
        raise ValueError(f"No dex table found at {url}; the page layout may have changed.")

    entries = []
    for row in table.find_all("tr"):
        cells = row.find_all("td", class_="fooinfo")
        if len(cells) >= 3 and (link := cells[2].find("a")):
            entries.append({
                "Number": int(cells[0].text.strip().lstrip("#")),
                "Name": link.text.strip(),
            })

    df = pd.DataFrame(entries).drop_duplicates()
    if df.empty:
        raise ValueError(f"Parsed 0 entries from {url}.")
    return df


def main():
    for filename, url in DEXES.items():
        df = scrape_dex(url)
        df.to_csv(filename, index=False)
        print(f"{filename}: {len(df):,} Pokémon (#{df.Number.min()} to #{df.Number.max()})")


if __name__ == "__main__":
    main()
