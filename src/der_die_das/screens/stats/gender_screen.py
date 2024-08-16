from der_die_das.database.models import GermanNounsGenderStats
from der_die_das.screens.stats.base_screen import StatsNounBaseScreen


class StatsGenderScreen(StatsNounBaseScreen):
    db_model = GermanNounsGenderStats
