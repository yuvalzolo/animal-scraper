import os
import re
import requests
import tempfile
from bs4 import BeautifulSoup
from typing import List
from animal_scraper.models import Animal


class WikipediaScraper:
    URL = "https://en.wikipedia.org/wiki/List_of_animal_names"

    def fetch_html(self) -> str:
        # Fetch and cache the Wikipedia page HTML locally
        cache_path = os.path.join(tempfile.gettempdir(), "animal_names_cache.html")
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

        response = requests.get(self.URL)
        response.raise_for_status()
        html = response.text

        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return html

    def clean_animal_name(self, raw_name: str) -> str:
        # Clean up animal names by removing refs, parentheses, etc.
        name = raw_name.strip()
        name = name.split('\n')[0]
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'\(.*?\)', '', name)
        name = re.sub(r'\|.*', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().title()

    def parse_adjectives(self, raw: str) -> List[str]:
        # Split multiple adjectives using common delimiters
        parts = re.split(r'[,\n/;]+', raw)
        return [part.strip().lower() for part in parts if part.strip()]

    def parse_animals(self, html: str) -> List[Animal]:
        # Parse the main tables on the Wikipedia page to extract animal names and adjectives
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})
        animals = []

        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue

            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['td', 'th'])]

            try:
                animal_col = headers.index("animal")
            except ValueError:
                try:
                    animal_col = headers.index("trivial name")
                except ValueError:
                    continue  # skip if no suitable column

            try:
                adjective_col = headers.index("collateral adjective")
            except ValueError:
                continue

            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) <= max(animal_col, adjective_col):
                    continue

                # Get animal name
                link = cols[animal_col].find('a')
                raw_name = link.text.strip() if link and link.text.strip() else cols[animal_col].text.strip()
                clean_name = self.clean_animal_name(raw_name)

                # Get adjectives
                raw_adjectives = cols[adjective_col].text.strip()
                adjectives = self.parse_adjectives(raw_adjectives)

                if clean_name and adjectives:
                    animals.append(Animal(clean_name, adjectives))

        return animals
