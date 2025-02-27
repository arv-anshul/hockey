import sys
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess

from .spiders import (
    CompetitionMatchesSpider,
    CompetitionsSpider,
    CompetitionTeamsSpider,
    MatchesDetailsSpider,
    PlayersSpider,
)

DATA_DIR = Path("data")
DEFAULT_SETTINGS = {
    "LOG_LEVEL": "WARNING",
}


def _set_spider_settings(spider: type[scrapy.Spider], settings: dict):
    """Add custom settings to spider, mainly for storing scraped data into files."""
    if spider.custom_settings is None:
        spider.custom_settings = {}
    spider.custom_settings.update(settings)
    return spider


def scrape_competitions(process: CrawlerProcess):
    """Scrape all the competitions available on the given altiusrt domain."""
    path = DATA_DIR / "competitions.json"
    if path.exists():
        return

    process.crawl(
        _set_spider_settings(
            CompetitionsSpider,
            {"FEEDS": {path: {"format": "json"}}},
        ),
        view_type="all",
    )


def scrape_competition_teams(process: CrawlerProcess, competition_id: int):
    """Scrape all the teams participating in given `competition_id`."""
    path = DATA_DIR / f"competition_{competition_id}/teams.json"
    if path.exists():
        return

    process.crawl(
        _set_spider_settings(
            CompetitionTeamsSpider,
            {"FEEDS": {path: {"format": "json"}}},
        ),
        competition_id=competition_id,
    )


def scrape_competition_matches(process: CrawlerProcess, competition_id: int):
    """Scrapes matches basic details which will be played in given `competition_id`."""
    path = DATA_DIR / f"competition_{competition_id}/matches.json"
    if path.exists():
        return

    process.crawl(
        _set_spider_settings(
            CompetitionMatchesSpider,
            {"FEEDS": {path: {"format": "json"}}},
        ),
        competition_id=competition_id,
    )


def scrape_players(process: CrawlerProcess, competition_id: int):
    """Scrapes all the players details participating in given `competition_id`."""
    path = DATA_DIR / f"competition_{competition_id}/players.jsonl"
    # Skip if already exists because players are not updated often
    if path.exists():
        return

    process.crawl(
        _set_spider_settings(
            PlayersSpider,
            {"FEEDS": {path: {"format": "jsonl", "overwrite": False}}},
        ),
        competition_id=competition_id,
    )


def scrape_matches_details(process: CrawlerProcess, competition_id: int):
    """Scrapes full details of matches which will be played in given `competition_id`."""
    path = DATA_DIR / f"competition_{competition_id}/matches_details.jsonl"

    process.crawl(
        _set_spider_settings(
            MatchesDetailsSpider,
            {"FEEDS": {path: {"format": "jsonl", "overwrite": True}}},
        ),
        competition_id=competition_id,
    )


def main(competition_id: int):
    process = CrawlerProcess(settings=DEFAULT_SETTINGS)

    # Scraped data stores in `data/` dir in structured way
    scrape_competitions(process)
    scrape_competition_teams(process, competition_id)
    scrape_competition_matches(process, competition_id)
    scrape_players(process, competition_id)
    scrape_matches_details(process, competition_id)

    process.start()


if __name__ == "__main__":
    try:
        competition_id = int(sys.argv[1])
    except IndexError:
        print("Please provide a competition_id as an argument.", file=sys.stderr)
        sys.exit(1)

    # run with: uv run python -m src.altiusrt.main 180
    main(competition_id)
