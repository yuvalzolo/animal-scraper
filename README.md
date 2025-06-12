🐾 Animal Collateral Adjective Scraper
This project scrapes the Wikipedia List of Animal Names and produces an HTML page that displays animals grouped by their collateral adjectives. It downloads an image for each animal from its corresponding Wikipedia page.

📌 Features
-Parses all animals and their collateral adjectives from the Wikipedia page.
-Handles multiple adjectives per animal.
-Downloads images from Wikipedia into /tmp/, with a fallback if no image is found.
-Generates a searchable HTML page with images and animal names grouped by adjective.
-Uses multithreading to speed up image downloading.
-Includes unit tests to validate core functionality.
-Modular structure suitable for production-level code.

🗂 Directory Structure
animal_scraper/
├── __init__.py
├── scraper.py          # Wikipedia parsing logic
├── image_downloader.py # Download images from Wikipedia
├── html_generator.py   # HTML output logic
├── models.py           # Animal model definition
tests/
└── test_scraper.py     # Unit tests
main.py                 # Entry point
README.md

🧪 Running the Code
# Create a virtual environment
poetry install

# Run the scraper
poetry run python -m animal_scraper.main

📸 Output
The HTML output is saved as output.html in the project root.
so you can open this file 

Images are saved both to:
/tmp/ (as required by the assignment)
output_images/ (for use by the HTML file)

🧪 Running the Tests
poetry run python -m unittest discover tests


🧠 Implementation Notes
-Threading is used in main.py via concurrent.futures.ThreadPoolExecutor to concurrently download images.
-Images are cached and saved with sanitized filenames.
-The scraper handles disambiguation pages and tries fallbacks (e.g., _(animal), _(bird)).
-HTML includes a JS-powered search box for filtering animals or adjectives.

🕒 Time Spent
~5 hours total