import os
import re
import shutil
from typing import List
from animal_scraper.models import Animal


class HTMLGenerator:
    def __init__(self, output_file='output.html', image_dir='output_images'):
        self.output_file = output_file
        self.image_dir = image_dir
        self.fallback_path = "/tmp/fallback.jpg"
        os.makedirs(self.image_dir, exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
        # Match logic used in ImageDownloader
        return re.sub(r'[\\/*?:"<>|]', '_', name.lower().replace(" ", "_"))

    def copy_image(self, source_path: str, dest_filename: str) -> str:
        dest_path = os.path.join(self.image_dir, dest_filename)
        if not os.path.exists(dest_path):
            try:
                shutil.copy2(source_path, dest_path)
            except Exception as e:
                print(f"[DEBUG] Failed to copy image {source_path} → {dest_path}: {e}")
        return dest_path

    def generate(self, animals: List[Animal]):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Animal Collateral Adjectives</title>
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0 20px;
        background: #fafafa;
    }
    h1 {
        text-align: center;
        margin-top: 30px;
    }
    h2 {
        margin-top: 40px;
        color: #2c3e50;
        border-bottom: 1px solid #ccc;
        padding-bottom: 5px;
    }
    .animal {
        margin: 10px 0 30px 20px;
        display: flex;
        align-items: center;
    }
    .animal img {
        width: 100px;
        height: auto;
        border-radius: 5px;
        margin-right: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .animal-name {
        font-weight: bold;
        font-size: 18px;
    }
    #search-box {
        margin: 20px auto;
        display: block;
        width: 300px;
        padding: 10px;
        font-size: 16px;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
</style>
<script>
    function filterAnimals() {
        const search = document.getElementById('search-box').value.toLowerCase();
        const adjectiveBlocks = document.querySelectorAll('.adjective-block');

        adjectiveBlocks.forEach(block => {
            const heading = block.querySelector('h2');
            const adjectiveText = heading.textContent.toLowerCase();
            const animals = block.querySelectorAll('.animal');
            let anyVisible = false;

            animals.forEach(animal => {
                const animalText = animal.textContent.toLowerCase();
                const isAnimalMatch = animalText.includes(search);
                const isAdjectiveMatch = adjectiveText.includes(search);
                const shouldShow = isAnimalMatch || isAdjectiveMatch;
                animal.style.display = shouldShow ? 'flex' : 'none';
                if (shouldShow) anyVisible = true;
            });

            block.style.display = anyVisible ? 'block' : 'none';
        });
    }
</script>
</head>
<body>
<h1>Animal Collateral Adjectives</h1>
<input type="text" id="search-box" onkeyup="filterAnimals()" placeholder="Search for an animal or adjective...">
''')

            # Group animals by adjective
            adjectives_map = {}
            for animal in animals:
                for adj in animal.adjectives:
                    adjectives_map.setdefault(adj, []).append(animal)

            # Generate HTML blocks
            for adj, animal_list in sorted(adjectives_map.items()):
                f.write(f'<div class="adjective-block">\n')
                f.write(f'<h2>{adj.capitalize()}</h2>\n')

                for animal in sorted(animal_list, key=lambda x: x.name):
                    safe_name = self.sanitize_filename(animal.name)
                    source_path = os.path.join("/tmp", f"{safe_name}.jpg")
                    if not os.path.exists(source_path):
                        print(f"[DEBUG] Using fallback for: {animal.name}")
                        source_path = self.fallback_path

                    dest_filename = f"{safe_name}.jpg"
                    self.copy_image(source_path, dest_filename)
                    img_path = os.path.join(self.image_dir, dest_filename).replace("\\", "/")

                    f.write(
                        f'<div class="animal">'
                        f'<a href="{img_path}" target="_blank">'
                        f'<img src="{img_path}" alt="{animal.name}" title="Click to view full image"></a>'
                        f'<div class="animal-name">{animal.name}</div>'
                        f'</div>\n'
                    )

                f.write('</div>\n')

            f.write('</body></html>')
