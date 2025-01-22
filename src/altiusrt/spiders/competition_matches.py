from __future__ import annotations

import re
import typing
from datetime import datetime  # noqa: TC003

import scrapy
from pydantic import BaseModel, ValidationError

if typing.TYPE_CHECKING:
    from parsel import Selector
    from scrapy.http.response import Response


class _CompetitionMatchDate(BaseModel):
    isoformat: datetime
    timezone: str


class CompetitionMatchModel(BaseModel):
    id: int
    competition_id: int
    match_number: int
    url: str
    scoreline: str | None
    match_type: str
    home_team: str
    away_team: str
    date: _CompetitionMatchDate
    venue: str


class CompetitionMatchesSpider(scrapy.Spider):
    name = "competition_matches"

    def __init__(
        self,
        competition_id: int,
        domain: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.domain = domain or "hockeyindia.altiusrt.com"
        self.competition_id = competition_id

    def start_requests(self):
        url = f"https://{self.domain}/competitions/{self.competition_id}/matches"
        yield scrapy.Request(url, self.parse_matches)

    def parse_matches(self, response: Response):
        rows = response.css(".tab-content table tbody tr")

        if len(rows) == 0 or (
            len(rows) == 1
            and any(
                i == rows[0].css("::text").get("").strip() for i in ("No results", "")
            )  # if any list-item satisfy then stop the scrapper
        ):
            self.logger.critical("No more results found. Stopping scraper.")
            return

        for row in rows:
            try:
                model_dict = self.parse_match_details(row)
                yield CompetitionMatchModel(url=response.url, **model_dict).model_dump()
            except ValidationError as e:
                self.logger.error(f"Validation failed for match: {e}")
            except ValueError as e:
                self.logger.error(f"Error fetching match: {e}")

    def parse_match_details(self, row: Selector) -> dict[str, typing.Any]:
        link = row.css("td:nth-child(3) a::attr(href)").get()
        if not link:
            raise ValueError(
                f"Cannot fetch title for competition {self.competition_id}",
            )
        match_id = link.split("/")[-1]

        title = row.css("td:nth-child(3) a::text").get("N/A").strip()
        result = re.match(
            r"^(?:([A-Za-z0-9/&' -]+) )?v ([A-Za-z0-9/&' -]+)?(?: \((.+)\))?$",
            title,
        )
        if not result:
            raise ValueError("Couldn't extract data from match title: " + title)

        scoreline = row.css("td:nth-child(4)::text").get("-").strip()

        return {
            "competition_id": self.competition_id,
            "scoreline": None if scoreline == "-" else scoreline,
            "id": match_id,
            "match_number": row.css("td:nth-child(1)::text").re_first(r"\d+", "-1"),
            "date": {
                "isoformat": row.css(
                    "td:nth-child(2) span[data-timezone]::attr(data-datetimelocal__notimechange)",
                )
                .get("N/A")
                .strip(),
                "timezone": row.css(
                    "td:nth-child(2) span[data-timezone]::attr(data-timezone)",
                )
                .get("N/A")
                .strip(),
            },
            "venue": row.css("td:nth-child(6)::text").get("N/A").strip(),
            "home_team": result.group(1) if result.group(1) else "",
            "away_team": result.group(2) if result.group(2) else "",
            "match_type": result.group(3) if result.group(3) else "",
        }
