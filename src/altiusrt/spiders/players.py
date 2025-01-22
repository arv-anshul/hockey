from __future__ import annotations

import typing

import scrapy
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from parsel import Selector
    from scrapy.http.response import Response


class PlayerModel(BaseModel):
    id: int
    team_id: int
    name: str
    shirt: int


class PlayersSpider(scrapy.Spider):
    name = "players"

    def __init__(
        self,
        team_id: int,
        domain: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.domain = domain or "hockeyindia.altiusrt.com"
        self.team_id = team_id

    def start_requests(self):
        yield scrapy.Request(
            f"https://{self.domain}/teams/{self.team_id}#players",
            self.parse,
        )

    def parse(self, response: Response):
        rows = response.css("#players table tr")[1:-1]  # remove thead > tr and last tr

        if len(rows) == 0 or (
            len(rows) == 1
            and any(
                i == rows[0].css("::text").get("").strip() for i in ("No results", "")
            )  # if any list-item satisfy then stop the scrapper
        ):
            self.logger.critical("No results found. Stopping scraper.")
            return

        yield from (PlayerModel(**self.parse_player(row)).model_dump() for row in rows)

    def parse_player(self, row: Selector) -> dict[str, typing.Any]:
        player_id = (
            row.css("td:nth-child(2) a::attr(href)")
            .get("-1")
            .strip()
            .rsplit("/", 1)[-1]
        )
        return {
            "id": player_id,
            "team_id": self.team_id,
            "name": row.css("td:nth-child(2) a::text").get("N/A").strip(),
            "shirt": row.css("td:nth-child(1) ::text").get("-1").strip(),
        }
