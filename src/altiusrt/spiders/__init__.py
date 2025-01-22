from .competition_matches import CompetitionMatchesSpider, CompetitionMatchModel
from .competition_teams import CompetitionTeamModel, CompetitionTeamsSpider
from .competitions import CompetitionModel, CompetitionsSpider
from .match_details import MatchDetailsModel, MatchesDetailsSpider
from .players import PlayerModel, PlayersSpider

__all__ = [
    "CompetitionMatchModel",
    "CompetitionMatchesSpider",
    "CompetitionModel",
    "CompetitionTeamModel",
    "CompetitionTeamsSpider",
    "CompetitionsSpider",
    "MatchDetailsModel",
    "MatchesDetailsSpider",
    "PlayerModel",
    "PlayersSpider",
]
