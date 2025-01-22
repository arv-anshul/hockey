from __future__ import annotations

import typing
from urllib.parse import parse_qs, urlparse

import scrapy
from pydantic import BaseModel, ValidationError
from scrapy import Request

if typing.TYPE_CHECKING:
    from parsel import Selector
    from scrapy.http.response import Response

ViewType = typing.Literal["upcoming", "previous", "inprogress"]


class CompetitionModel(BaseModel):
    index: int
    id: int
    name: str
    competition_type: str
    location: str
    date: str
    total_matches: int
    url: str


class CompetitionsSpider(scrapy.Spider):
    name = "competitions"

    def __init__(
        self,
        view_type: ViewType | typing.Literal["all"],
        domain: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.domain = domain or "hockeyindia.altiusrt.com"
        self.view_type = view_type
        self.start_page = 1
        self.index = 0

    def _request_next_page(self, response: Response) -> Request:
        next_page = response.meta["page"] + 1
        current_view = parse_qs(urlparse(response.url).query)["view"][0]
        return Request(
            f"https://{self.domain}/competitions?view={current_view}&page={next_page}",
            callback=self.parse,
            meta={"page": next_page},
        )

    def start_requests(self):
        # We'll not scrape 'view=all' page because it contains almost all the
        # competitions present on the website which might be irrelevant.
        views = [self.view_type] if self.view_type != "all" else list(ViewType.__args__)
        for view_type in views:
            yield Request(
                f"https://{self.domain}/competitions?view={view_type}&page={self.start_page}",
                callback=self.parse,
                meta={"page": self.start_page},
            )

    def parse(self, response: Response):
        rows = response.css("#admin_list_of_competitions table tbody tr")
        if len(rows) == 0 or (
            len(rows) == 1
            and any(
                i == rows[0].css("::text").get("").strip() for i in ("No results", "")
            )  # if any list-item satisfy then stop the scrapper
        ):
            self.logger.critical(
                f"No more results found for {response.url!r}. Stopping scraper.",
            )
            return

        for row in rows:
            self.index += 1  # increase index for each competition
            try:
                competition = CompetitionModel(
                    url=response.url,
                    **self.parse_competition_details(row),
                )
                yield competition.model_dump()
            except ValidationError as e:
                self.logger.error(f"Validation failed for competition: {e}")

        # Continue pagination
        yield self._request_next_page(response)

    def parse_competition_details(self, row: Selector) -> dict[str, typing.Any]:
        link = row.css("td:nth-child(2) a::attr(href)").get()
        competition_id = link.rsplit("/", 1)[-1] if link else None

        return {
            "index": self.index,
            "id": competition_id,
            "name": row.css("td:nth-child(2) a::text").get("N/A").strip(),
            "competition_type": row.css("td:nth-child(5)::text").get("N/A").strip(),
            "location": row.css("td:nth-child(4)::text").get(),
            "date": "".join(row.css("td:nth-child(3) *::text").getall()).strip(),
            "total_matches": row.css("td:nth-child(6)::text").get(),
        }
