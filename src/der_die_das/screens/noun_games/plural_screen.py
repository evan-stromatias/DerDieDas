import random

from der_die_das.database.models import GermanNounsPluralStats
from der_die_das.screens.noun_games.base_screen import NounGamesBaseScreen


class NounPluralScreen(NounGamesBaseScreen):
    db_model = GermanNounsPluralStats

    def check_answer_logic(self, answer: str) -> bool:
        return answer.lower() == self.noun_db_entry.plural.lower()

    def generate_question_text(self):
        return f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}. Die ..."

    def generate_positive_feedback_text(self) -> str:
        return f"JA! Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-','')}."

    def generate_negative_feedback_text(self) -> str:
        return f"NEIN! Die {self.noun_db_entry.noun}{self.noun_db_entry.plural.replace('-', '')}."

    def update_button_labels(self):
        options = self.update_plural_options()
        self.button_1.text = options[0]
        self.button_2.text = options[1]
        self.button_3.text = options[2]

    def random_noun_row(self):
        while True:
            rnd_row = super().random_noun_row()
            if "-" in rnd_row.plural:
                return rnd_row

    def update_plural_options(self):
        options = [self.noun_db_entry.plural]

        while len(options) < self.TOTAL_OPTIONS_ANSWERS:
            rnd_noun = super().random_noun_row()
            if rnd_noun.plural not in options and "-" in rnd_noun.plural:
                options.append(rnd_noun.plural)

        random.shuffle(options)
        return options
