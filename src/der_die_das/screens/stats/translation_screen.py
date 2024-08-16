from der_die_das.database.models import GermanNounsTranslationStats
from der_die_das.screens.stats.base_screen import StatsNounBaseScreen


class StatsTranslationScreen(StatsNounBaseScreen):
    db_model = GermanNounsTranslationStats
