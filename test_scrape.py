name: Test Scrape

on:
  workflow_dispatch:

jobs:
  run-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Poetry
        run: |
          python -m pip install --upgrade pip
          pip install poetry

      - name: Install dependencies
        run: poetry install --no-root  # ← ここが重要！

      - name: Run scraping test
        run: poetry run python test_scrape.py
