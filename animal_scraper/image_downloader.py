import os
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

class ImageDownloader:
    def __init__(self, output_dir='/tmp'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download_image(self, animal_name: str) -> str:
        search_url = f"https://en.wikipedia.org/wiki/{quote(animal_name)}"
        try:
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            image = soup.find('table', {'class': 'infobox'}).find('img')
            if image:
                image_url = "https:" + image['src']
                image_data = requests.get(image_url).content
                file_path = os.path.join(self.output_dir, f"{animal_name}.jpg")
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                return file_path
        except Exception:
            pass
        return None  # fallback if no image found
