name: Scrape G大阪 Match Info

on:
  schedule:
    - cron: '0 0 * * *'  # 毎日午前9時に自動実行
  workflow_dispatch:     # 手動実行もOK

permissions:
  contents: write

jobs:
  scrape-job:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests  # 👈 ここだけ追加！

      - name: Run scrape script
        run: python job_scrape.py

      - name: Commit and push match_info.txt
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add cache/match_info.txt
          git commit -m "Update G大阪 match info" || echo "No changes to commit"
          git push
