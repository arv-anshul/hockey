# Scrape Hockey Data

<p align="center">
  <img src="https://img.shields.io/badge/Scrapy-60A839?logo=scrapy&logoColor=fff" alt="Scrapy">
  <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff" alt="Pydantic">
</p>

This project is used to scrape data related to **Hockey** from [altiusrt.com](https://altiusrt.com). I mainly focused on
[hockeyindia.altiusrt.com](https://hockeyindia.altiusrt.com) because I am interested in **Hockey India League** (HIL).

For now, scraper is able scrape following data:

1. **Competitions:** Details about **previous, upcoming and inprogress** competitions. _Competitions are like a
   tournament (eg. **Hockey India League**)._
2. **Competition Teams:** Details about teams participated in the competition.
3. **Competition Matches:** Details about specified competition's matches.
4. **Competition Players:** Details about players who will be playing the competition.
5. **Competition Matches** (detailed): A full detailed data around the match like umpires, players who goal, quater-wise
   data and more.

You can use [`altiusrt/main.py`](src/altiusrt/main.py) to scrape the data related to a specific competition (eg.
**HIL**) and export them into `json` and `jsonl` (aka `jsonlines`) data format.

```bash
uv run python -m src.altiusrt.main 180
```

> In above command, **`180`** is the `competition_id` for **Hockey India League** competition/tournament.
