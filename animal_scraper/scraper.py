import requests
from bs4 import BeautifulSoup
from typing import List
from animal_scraper.models import Animal

class WikipediaScraper:
    URL = "https://en.wikipedia.org/wiki/List_of_animal_names"

    def fetch_html(self) -> str:
        response = requests.get(self.URL)
        response.raise_for_status()
        return response.text

    def parse_animals(self, html: str) -> List[Animal]:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})
        animals = []
        for table in tables:
            for row in table.find_all('tr')[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 7:
                    continue
                animal_name = cols[0].text.strip()
                adjectives_raw = cols[6].text.strip()
                adjectives = [adj.strip() for adj in adjectives_raw.split(',') if adj.strip()]
                if animal_name and adjectives:
                    animals.append(Animal(animal_name, adjectives))
        return animals
