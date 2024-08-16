from der_die_das.database.models import GermanNounsPluralStats
from der_die_das.screens.stats.base_screen import StatsNounBaseScreen


class StatsPluralScreen(StatsNounBaseScreen):
    db_model = GermanNounsPluralStats
