import os
import re
import requests
from pathlib import Path
from urllib.parse import quote
from bs4 import BeautifulSoup


class ImageDownloader:
    def __init__(self, output_dir='/tmp'):
        # Create output directory for images
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fallback_path = self.output_dir / "fallback.jpg"
        self.ensure_fallback_image()
        self.cache = {}  # Cache to avoid re-downloading

    def ensure_fallback_image(self):
        # Downloads a placeholder image if not already available
        if not self.fallback_path.exists():
            fallback_url = "https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg"
            try:
                response = requests.get(fallback_url, timeout=10)
                self.fallback_path.write_bytes(response.content)
                print("[DEBUG] Fallback image downloaded")
            except Exception as e:
                print(f"[DEBUG] Failed to download fallback image: {e}")

    def is_disambiguation_page(self, soup):
        # Check if the page is a disambiguation page by HTML structure or text
        return bool(soup.select("table.ambox-disambig, .mw-disambig")) or "may refer to:" in soup.get_text().lower()

    def follow_first_valid_link(self, soup):
        # Navigate to first valid link on a disambiguation page
        for li in soup.select(".mw-parser-output ul li a"):
            href = li.get("href", "")
            if href.startswith("/wiki/") and not any(x in href for x in [":", "#"]):
                print(f"[DEBUG] Found redirect link: {href}")
                return f"https://en.wikipedia.org{href}"
        return None

    def resolve_disambiguation(self, animal_name):
        # Uses Wikipedia search to resolve ambiguous terms
        search_query_url = f"https://en.wikipedia.org/w/index.php?search={quote(animal_name)}"
        try:
            resp = requests.get(search_query_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            link = soup.select_one(".mw-search-result-heading a") or soup.select_one("p a")
            if link:
                href = link['href']
                print(f"[DEBUG] Disambiguation resolved for {animal_name} to {href}")
                return f"https://en.wikipedia.org{href}"
        except Exception as e:
            print(f"[DEBUG] Error during disambiguation for {animal_name}: {e}")
        return None

    def try_suffix_fallbacks(self, animal_name):
        # Try fallback URLs by appending suffixes like _(animal) or _(bird)
        suffixes = ["_(bird)", "_(animal)", "_(mammal)", "_(fish)"]
        for suffix in suffixes:
            candidate = f"https://en.wikipedia.org/wiki/{quote(animal_name + suffix)}"
            try:
                print(f"[DEBUG] Trying suffix fallback: {candidate}")
                response = requests.get(candidate, timeout=10)
                if response.ok:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_url = self.get_valid_image_url(soup)
                    if image_url:
                        return image_url
            except Exception as e:
                print(f"[DEBUG] Failed suffix fallback for {candidate}: {e}")
        return None

    def get_valid_image_url(self, soup):
        # Look for a high-res image in infobox, reconstruct full image URL from thumbnail
        def is_valid(src):
            invalid_keywords = [
                "wiktionary", "disambig", "question_book", "ambox", "commons-logo",
                "p_vip", "wikidata-logo", "wikispecies-logo", "edit", "icon"
            ]
            src_lower = src.lower()
            return (
                    ("upload.wikimedia.org" in src_lower or src.startswith("//upload.wikimedia.org")) and
                    not any(kw in src_lower for kw in invalid_keywords) and
                    not src_lower.endswith(".svg") and
                    not src_lower.endswith(".svg.png")
            )

        for img in soup.select("table.infobox img"):
            src = img.get("src", "")
            print(f"[DEBUG] Found image candidate: {src}")
            if not is_valid(src):
                print(f"[DEBUG] Rejected image: {src}")
                continue

            # ✅ Handle thumbnail reconstruction
            try:
                if "/thumb/" in src:
                    thumb_parts = src.split("/thumb/")
                    path_parts = thumb_parts[1].split("/")
                    file_path = "/".join(path_parts[0:2])
                    # Safely extract filename after last px- (case-insensitive)
                    filename_parts = path_parts[-1].split("px-")
                    if len(filename_parts) > 1:
                        filename = filename_parts[1]
                    else:
                        filename = path_parts[-1]
                    highres_src = f"/wikipedia/commons/{file_path}/{filename}"
                    full_url = "https://upload.wikimedia.org" + highres_src
                else:
                    full_url = "https:" + src if src.startswith("//") else src
            except Exception as e:
                print(f"[DEBUG] Failed to reconstruct image, using original: {e}")
                full_url = "https:" + src if src.startswith("//") else src

            print(f"[DEBUG] Accepted image: {full_url}")
            return full_url

        # Fallback to other images if no valid infobox image
        for img in soup.select("img"):
            src = img.get("src", "")
            if is_valid(src):
                full_url = "https:" + src if src.startswith("//") else src
                print(f"[DEBUG] Fallback accepted image: {full_url}")
                return full_url

        return None

    def safe_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', '_', name.lower().replace(" ", "_"))

    def download_image(self, animal_name: str) -> str:
        # Main logic to download an animal image from Wikipedia.
        # Handles redirects, disambiguation, suffix fallbacks, and ensures caching.
        if animal_name in self.cache:
            return self.cache[animal_name]

        safe_name = self.safe_filename(animal_name)
        file_path = self.output_dir / f"{safe_name}.jpg"
        if file_path.exists():
            self.cache[animal_name] = str(file_path)
            return str(file_path)

        normalized = "_".join([word.lower() for word in animal_name.split()])
        normalized = normalized[0].upper() + normalized[1:]
        search_url = f"https://en.wikipedia.org/wiki/{normalized}"
        print(f"[DEBUG] Searching for {animal_name} at {search_url}")

        try:
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            image_url = self.get_valid_image_url(soup)

            if not image_url and self.is_disambiguation_page(soup):
                redirect_url = self.follow_first_valid_link(soup)
                if redirect_url:
                    print(f"[DEBUG] Redirecting from disambiguation page to: {redirect_url}")
                    response = requests.get(redirect_url, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_url = self.get_valid_image_url(soup)

            if not image_url:
                print(f"[DEBUG] No valid image found for {animal_name}, trying fallback...")
                redirect_url = self.resolve_disambiguation(animal_name)
                if redirect_url:
                    response = requests.get(redirect_url, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_url = self.get_valid_image_url(soup)

            if not image_url and self.is_disambiguation_page(soup):
                redirect_url = self.follow_first_valid_link(soup)
                if redirect_url:
                    print(f"[DEBUG] Final redirect retry for disambiguation: {redirect_url}")
                    response = requests.get(redirect_url, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_url = self.get_valid_image_url(soup)

            # ✅ Try suffix-based fallback
            if not image_url:
                image_url = self.try_suffix_fallbacks(animal_name)

            if image_url:
                print(f"[DEBUG] Downloading image from: {image_url}")
                headers = {
                    "User-Agent": "animal-scraper/1.0 (https://example.com/; contact@example.com)"
                }
                response = requests.get(image_url, headers=headers, timeout=10)
                response.raise_for_status()

                # Optional sanity check
                if "image" not in response.headers.get("Content-Type", ""):
                    print("[DEBUG] URL did not return an image.")
                    raise ValueError("URL did not return an image")

                file_path.write_bytes(response.content)
                self.cache[animal_name] = str(file_path)
                return str(file_path)

        except Exception as e:
            print(f"[DEBUG] Error downloading image for {animal_name}: {e}")

        print(f"[DEBUG] Still no image found for {animal_name}")
        self.cache[animal_name] = str(self.fallback_path)
        return str(self.fallback_path)
