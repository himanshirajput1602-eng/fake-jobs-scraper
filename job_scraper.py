"""
job_scraper.py
Scrapes job listings from https://realpython.github.io/fake-jobs/
and saves results to jobs.csv
"""

import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://realpython.github.io/fake-jobs/"
OUTPUT_FILE = "jobs.csv"
FIELDNAMES = ["title", "company", "location", "url"]


def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None


def parse_jobs(soup: BeautifulSoup) -> list[dict]:
    """Extract job listings from the page soup."""
    jobs = []

    cards = soup.select("div.card-content")
    if not cards:
        print("[WARNING] No job cards found on the page.")
        return jobs

    for card in cards:
        title = card.select_one("h2.title")
        company = card.select_one("h3.company")
        location = card.select_one("p.location")

        # Find the "Apply" link inside the parent card
        parent = card.parent  # <div class="card">
        apply_link = parent.select_one("a[href]") if parent else None

        # Safely extract text / href, falling back to empty string
        job = {
            "title":   title.get_text(strip=True)   if title   else "",
            "company": company.get_text(strip=True) if company else "",
            "location": location.get_text(strip=True) if location else "",
            "url":     apply_link["href"]            if apply_link else "",
        }

        jobs.append(job)

    return jobs


def save_to_csv(jobs: list[dict], filename: str) -> None:
    """Write a list of job dicts to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"[OK] Saved {len(jobs)} jobs to '{filename}'")


def main() -> None:
    print(f"[*] Fetching jobs from {BASE_URL} ...")
    soup = fetch_page(BASE_URL)
    if soup is None:
        print("[ABORT] Could not retrieve the page.")
        return

    jobs = parse_jobs(soup)
    print(f"[*] Found {len(jobs)} job listings.")

    if jobs:
        save_to_csv(jobs, OUTPUT_FILE)


if __name__ == "__main__":
    main()
