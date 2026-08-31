import csv
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup
#BASE_URL = "https://archive.org/download/playstation2_essentials"
#BASE_URL = "https://archive.org/download/atari-2600-roms-ultra"
#BASE_URL = "https://archive.org/download/C64RomCollectionByGhostware"
BASE_URL = "https://archive.org/download/GameboyAdvanceRomCollectionByGhostware"
#OUTPUT_FILE = "PS2_links.csv"
#OUTPUT_FILE = "atari_links.csv"
#OUTPUT_FILE = "C64_links.csv"
OUTPUT_FILE = "Gameboy_links.csv"



def get_links():
    response = requests.get(
        BASE_URL + "/",
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for anchor in soup.select("a[href]"):
        href = anchor["href"]

        # Pomijamy linki nawigacyjne i zewnętrzne
        if href.startswith(("http://", "https://", "#", "../", "/")):
            continue

        filename = unquote(urlparse(href).path)

        # Tylko obrazy dyskietek .D64
        #if not filename.lower().endswith(".d64"):
        #    continue
            
        # Tylko obrazy dyskietek .bin
        #if not filename.lower().endswith(".bin"):
        #    continue
        
        # Tylko obrazy dyskietek .iso
        #if not filename.lower().endswith(".iso"):
        #    continue
        
        # Tylko obrazy dyskietek .zip
        if not filename.lower().endswith(".zip"):
            continue

        full_url = urljoin(BASE_URL + "/", href)

        links.append({
            "filename": filename,
            "url": full_url,
        })

    # Usunięcie ewentualnych duplikatów
    unique_links = {}
    for link in links:
        unique_links[link["url"]] = link

    return list(unique_links.values())


def main():
    links = get_links()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["filename", "url"])
        writer.writeheader()
        writer.writerows(links)

    print(f"Znaleziono: {len(links)} plików")
    print(f"Zapisano do: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()