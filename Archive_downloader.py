import argparse
import csv
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup


def get_item_name(base_url):
    path = urlparse(base_url).path.rstrip("/")
    parts = path.split("/")

    try:
        download_index = parts.index("download")
        return parts[download_index + 1]
    except (ValueError, IndexError):
        raise ValueError(
            "BASE_URL must be in the format: https://archive.org/download/nazwa_zbioru"
        )


def get_links(base_url, extensions=None):
    response = requests.get(
        base_url.rstrip("/") + "/",
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

        parsed_href = urlparse(href)

        # Pomijamy podkatalogi
        if parsed_href.path.endswith("/"):
            continue

        filename = unquote(parsed_href.path)

        # Opcjonalne filtrowanie rozszerzeń
        if extensions:
            if not filename.lower().endswith(
                tuple("." + ext.lower().lstrip(".") for ext in extensions)
            ):
                continue

        full_url = urljoin(base_url.rstrip("/") + "/", href)

        links.append({
            "filename": filename,
            "url": full_url,
        })

    # Usunięcie duplikatów
    unique_links = {
        link["url"]: link
        for link in links
    }

    return list(unique_links.values())


def main():
    parser = argparse.ArgumentParser(
        description="Retrieves file links from the Internet Archive directory."
    )

    parser.add_argument(
        "base_url",
        help="URL path, np. https://archive.org/download/playstation2_essentials",
    )

    parser.add_argument(
        "--ext",
        nargs="+",
        help="Optional file types, e.g. --ext zip iso bin",
    )

    args = parser.parse_args()

    item_name = get_item_name(args.base_url)
    output_file = f"{item_name}.csv"

    links = get_links(args.base_url, args.ext)

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["filename", "url"])
        writer.writeheader()
        writer.writerows(links)

    print(f"Found: {len(links)} files")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()