from __future__ import annotations

import json
import typing

import scrapy
from pydantic import BaseModel, ValidationError
from scrapy import Request

if typing.TYPE_CHECKING:
    from scrapy.http.response import Response


class _MatchTeam(BaseModel):
    id: int
    name: str
    code: str
    organization_id: int


class _MatchOfficial(BaseModel):
    id: int
    person_id: int
    role: str
    displayname: str
    medianame: str


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
    hometeam: _MatchTeam
    awayteam: _MatchTeam
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
            url = f"https://{self.domain}/rt/matches/{match_id}?embeds=statistics,hometeam,awayteam"
            yield Request(url, self.parse)

    def parse(self, response: Response):
        try:
            match = MatchDetailsModel(url=response.url, **json.loads(response.text))
            yield match.model_dump()
        except ValidationError as e:
            self.logger.error(f"Validation failed for match: {e}")
        except ValueError as e:
            self.logger.error(f"Error fetching match: {e}")
