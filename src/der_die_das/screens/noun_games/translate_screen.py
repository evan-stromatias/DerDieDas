import random

from der_die_das.database.db_instance import db
from der_die_das.database.models import GermanNounsTranslationStats
from der_die_das.screens.noun_games.base_screen import NounGamesBaseScreen


class NounTranslateScreen(NounGamesBaseScreen):
    db_model = GermanNounsTranslationStats

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_noun = False

    def check_answer_logic(self, answer: str) -> bool:
        return answer.lower() == self.noun_db_entry.translation.lower()

    def generate_question_text(self):
        return f"{self.noun_db_entry.gender} {self.noun_db_entry.noun}"

    def generate_positive_feedback_text(self) -> str:
        return f"Yes! {self.noun_db_entry.translation}"

    def generate_negative_feedback_text(self) -> str:
        return f"No! {self.noun_db_entry.translation}"

    def update_button_labels(self):
        options = self.update_plural_options()
        self.button_1.text = options[0]
        self.button_2.text = options[1]
        self.button_3.text = options[2]

    def update_plural_options(self):
        options = [self.noun_db_entry.translation]
        random_nouns = db.random_rows(self.TOTAL_OPTIONS_ANSWERS - len(options))
        for rn in random_nouns:
            print(rn)
            options.append(rn[0].translation)

        random.shuffle(options)
        return options
