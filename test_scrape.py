name: Test Scrape

on:
  workflow_dispatch:

jobs:
  run-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.10

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies (no-root)
        run: poetry install --no-root

      - name: Run scraping test
        run: poetry run python test_scrape.py
