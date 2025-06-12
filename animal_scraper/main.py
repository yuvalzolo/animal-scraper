from animal_scraper.scraper import WikipediaScraper
from animal_scraper.image_downloader import ImageDownloader
from animal_scraper.html_generator import HTMLGenerator
from concurrent.futures import ThreadPoolExecutor, as_completed


def download_images_concurrently(animal_objects, downloader, max_workers=10):
    # Uses a thread pool to download images concurrently
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_animal = {
            executor.submit(downloader.download_image, animal.name): animal for animal in animal_objects
        }
        for future in as_completed(future_to_animal):
            animal = future_to_animal[future]
            try:
                image_path = future.result()
                animal.image_path = image_path.lower()
                results[animal.name] = image_path
                print(f"[THREAD] Downloaded: {animal.name} → {image_path}")
            except Exception as e:
                print(f"[THREAD] Failed for {animal.name}: {e}")
                animal.image_path = str(downloader.fallback_path)

    return results


def main():
    # Orchestrates the flow: scrape → download → generate HTML
    scraper = WikipediaScraper()
    html = scraper.fetch_html()
    animals = scraper.parse_animals(html)
    downloader = ImageDownloader()
    download_images_concurrently(animals, downloader)

    html_gen = HTMLGenerator()
    html_gen.generate(animals)


if __name__ == "__main__":
    main()
