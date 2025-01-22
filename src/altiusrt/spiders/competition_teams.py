from __future__ import annotations

import typing

import scrapy
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from parsel import Selector
    from scrapy.http.response import Response


class CompetitionTeamModel(BaseModel):
    id: int
    name: str
    code: str


class CompetitionTeamsSpider(scrapy.Spider):
    name = "competition_teams"

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
        url = f"https://{self.domain}/competitions/{self.competition_id}/teams"
        yield scrapy.Request(url, self.parse)

    def parse(self, response: Response):
        rows = response.css(".tab-content table tbody tr")

        if len(rows) == 0 or (
            len(rows) == 1
            and any(
                i == rows[0].css("::text").get("").strip() for i in ("No results", "")
            )  # if any list-item satisfy then stop the scrapper
        ):
            self.logger.critical("No more results found. Stopping scraper.")
            return

        yield from (
            CompetitionTeamModel(**self.parse_team_details(row)).model_dump()
            for row in rows
        )

    def parse_team_details(self, row: Selector) -> dict[str, typing.Any]:
        team_id = (
            row.css("td:nth-child(1) ::attr(href)").get("-1").strip().rsplit("/", 1)[-1]
        )
        return {
            "id": team_id,
            "name": row.css("td:nth-child(1) ::text").get("N/A").strip(),
            "code": row.css("td:nth-child(2) ::text").get("N/A").strip(),
        }
