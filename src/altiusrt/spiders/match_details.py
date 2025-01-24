from __future__ import annotations

import json
import typing

import scrapy
from pydantic import BaseModel, ValidationError
from scrapy import Request

if typing.TYPE_CHECKING:
    from scrapy.http.response import Response


class _MatchOfficial(BaseModel):
    id: int
    person_id: int
    role: str
    displayname: str
    medianame: str


class _MatchGoal(BaseModel):
    id: int
    match_id: int
    seconds: float
    team_id: int
    event: str
    player_id: int
    defender_id: int | None = None
    official_id: int | None = None
    type: str | None = None
    outcome: str | None = None
    minutedisp: str


class MatchDetailsModel(BaseModel):
    id: int
    url: str
    competition_id: int
    status: typing.Literal["Official", "Upcoming"]
    number: int
    title: str | None = None
    poolstext: str
    venue: str
    pitch_id: int
    hometeam_id: int
    awayteam_id: int
    homescore: int
    awayscore: int
    homeps: int
    awayps: int
    U1: _MatchOfficial
    U2: _MatchOfficial
    period_short: str
    period_minutes: float
    period_count: int
    shootout_count: int
    goals: list[_MatchGoal]
    statistics: dict[str, typing.Any]


class MatchesDetailsSpider(scrapy.Spider):
    name = "match_details"

    def __init__(
        self,
        match_ids: list[int],
        domain: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.domain = domain or "hockeyindia.altiusrt.com"
        self.match_ids = match_ids

    def start_requests(self):
        for match_id in self.match_ids:
            url = f"https://{self.domain}/rt/matches/{match_id}?embeds=statistics,goals"
            yield Request(url, self.parse)

    def parse(self, response: Response):
        try:
            match = MatchDetailsModel(url=response.url, **json.loads(response.text))
            yield match.model_dump()
        except ValidationError as e:
            self.logger.error(f"Validation failed for match: {e}")
        except ValueError as e:
            self.logger.error(f"Error fetching match: {e}")
