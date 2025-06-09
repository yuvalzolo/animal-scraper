from animal_scraper.models import Animal
from typing import List


class HTMLGenerator:
    def __init__(self, output_file='output.html'):
        self.output_file = output_file

    def generate(self, animals: List[Animal]):
        with open(self.output_file, 'w') as f:
            f.write('<html><body>\n')
            adjectives_map = {}
            for animal in animals:
                for adj in animal.adjectives:
                    adjectives_map.setdefault(adj, []).append(animal)
            for adj, animal_list in adjectives_map.items():
                f.write(f"<h2>{adj}</h2>\n<ul>\n")
                for animal in animal_list:
                    img_path = f"/tmp/{animal.name}.jpg"
                    f.write(f"<li>{animal.name} <img src='{img_path}' width='100'></li>\n")
                f.write("</ul>\n")
            f.write('</body></html>\n')
