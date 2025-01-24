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
        yield scrapy.Request(url, self.parse_team_ids)

    def parse_team_ids(self, response: Response):
        rows = response.css(".tab-content table tbody tr")

        team_ids = []
        for row in rows:
            team_id = row.css("td:nth-child(1) ::attr(href)").get()
            if not team_id:
                msg = f"Error while parsing team_id for player {self.competition_id}"
                raise ValueError(msg)
            team_ids.append(team_id.strip().rsplit("/", 1)[-1])

        # iterate over team_ids and fetch player details
        for team_id in team_ids:
            yield scrapy.Request(
                f"https://{self.domain}/teams/{team_id}#players",
                self.parse_players,
                cb_kwargs={"team_id": int(team_id)},
            )

    def parse_players(self, response: Response, team_id: int):
        rows = response.css("#players table tr")[1:-1]  # remove thead > tr and last tr

        if len(rows) == 0 or (
            len(rows) == 1
            and any(
                i == rows[0].css("::text").get("").strip() for i in ("No results", "")
            )  # if any list-item satisfy then stop the scrapper
        ):
            self.logger.critical("No results found. Stopping scraper.")
            return

        yield from (
            PlayerModel(team_id=team_id, **self.parse_player(row)).model_dump()
            for row in rows
        )

    def parse_player(self, row: Selector) -> dict[str, typing.Any]:
        player_id = (
            row.css("td:nth-child(2) a::attr(href)")
            .get("-1")
            .strip()
            .rsplit("/", 1)[-1]
        )
        return {
            "id": player_id,
            "name": row.css("td:nth-child(2) a::text").get("N/A").strip(),
            "shirt": row.css("td:nth-child(1) ::text").get("-1").strip(),
        }
